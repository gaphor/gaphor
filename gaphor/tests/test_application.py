#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
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
"""Application service test cases."""

from __future__ import absolute_import

import unittest
from zope import component

from gaphor.application import Application
from gaphor.interfaces import IService


class LoadServiceTestCase(unittest.TestCase):
    """Test case for loading Gaphor services."""

    def test_service_load(self):
        """Test loading services and querying utilities."""

        Application.init(['undo_manager', 'file_manager', 'properties'])

        self.assertTrue(Application.get_service('undo_manager') is not None, 'Failed to load the undo manager service')

        self.assertTrue(Application.get_service('file_manager') is not None, 'Failed to load the file manager service')

        self.assertTrue(component.queryUtility(IService, 'undo_manager') is not None, (
            'Failed to query the undo manager utility'))

        self.assertTrue(component.queryUtility(IService, 'file_manager') is not None, (
            'Failed to query the file manager utility'))

        Application.shutdown()
