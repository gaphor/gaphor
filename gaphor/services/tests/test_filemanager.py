#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License
# more details.
#
# You should have received a copy of the GNU Library General Public
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
import unittest
from gaphor.application import Application
from six.moves import range


class FileManagerTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['file_manager', 'element_factory', 'properties', 'main_window', 'action_manager', 'ui_manager'])
        self.recent_files_backup = Application.get_service('properties').get('recent-files')

    def tearDown(self):
        Application.get_service('properties').set('recent-files', self.recent_files_backup)
        Application.shutdown()

    def test_recent_files(self):
        fileman = Application.get_service('file_manager')
        properties = Application.get_service('properties')

        # ensure the recent_files list is empty:
        properties.set('recent-files', [])
        fileman.update_recent_files()
        for i in range(0, 9):
            a = fileman.action_group.get_action('file-recent-%d' % i)
            assert a
            assert a.get_property('visible') == False, '%s, %d' % (a.get_property('visible'), i)

        fileman.filename = 'firstfile'
        a = fileman.action_group.get_action('file-recent-%d' % 0)
        assert a
        assert a.get_property('visible') == True
        assert a.props.label == '_1. firstfile', a.props.label
        for i in range(1, 9):
            a = fileman.action_group.get_action('file-recent-%d' % i)
            assert a
            assert a.get_property('visible') == False

