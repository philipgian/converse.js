# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2014 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Minimal distributed version control system abstraction for Weblate needs.
"""
import subprocess


class RepositoryException(Exception):
    """
    Error while working with a repository.
    """


class Repository(object):
    """
    Basic repository object.
    """
    _last_revision = None
    _last_remote_revision = None
    _cmd = 'false'
    _cmd_last_revision = []
    _cmd_last_remote_revision = []
    _cmd_clone = 'clone'

    def __init__(self, path):
        self.path = path

    @classmethod
    def _popen(cls, args, cwd=None):
        args.insert(0, cls._cmd)
        process = subprocess.Popen(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, output_err = process.communicate()
        retcode = process.poll()
        if retcode:
            raise RepositoryException(output_err)
        return output

    def _execute(self, args):
        return self._popen(args, self.path)

    @property
    def last_revision(self):
        if self._last_revision is None:
            self._last_revision = self._execute(
                self._cmd_last_revision
            )
        return self._last_revision

    @property
    def last_remote_revision(self):
        if self._last_remote_revision is None:
            self._last_remote_revision = self._execute(
                self._cmd_last_remote_revision
            )
        return self._last_remote_revision

    @classmethod
    def clone(cls, source, target):
        """
        Clones repository and returns Repository object for cloned
        repository.
        """
        cls._popen([cls._cmd_clone, source, target])
        return cls(target)


class GitRepository(Repository):
    """
    Repository implementation for Git.
    """
    _cmd = 'git'
    _cmd_last_revision = [
        'log', '-n', '1', '--format=format:%H', '@'
    ]
    _cmd_last_remote_revision = [
        'log', '-n', '1', '--format=format:%H', '@{upstream}'
    ]
