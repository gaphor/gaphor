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

        self.assertTrue(Application.get_service('undo_manager') is not None, \
                        'Failed to load the undo manager service')

        self.assertTrue(Application.get_service('file_manager') is not None, \
                        'Failed to load the file manager service')

        self.assertTrue(component.queryUtility(IService, 'undo_manager') is not None, \
                        'Failed to query the undo manager utility')

        self.assertTrue(component.queryUtility(IService, 'file_manager') is not None, \
                        'Failed to query the file manager utility')

        Application.shutdown()
