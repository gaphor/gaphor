"""Unittest the storage and parser modules
"""

import os
import unittest
from gaphor import UML
from gaphor.application import Application
from zope import component
from gaphor.interfaces import IService


class StorageTestCase(unittest.TestCase):

    def tearDown(self):
        pass

    def test_service(self):
        """
        Load services. At lease the undo_manager should be available after that.
        """
        
        Application.load_services()
        assert Application.get_service('undo_manager')
        assert Application.get_service('plugin_manager')

        # After that, services are also available as Utilities:
        assert component.queryUtility(IService, 'undo_manager')
        assert component.queryUtility(IService, 'plugin_manager')


# vim:sw=4:et:ai
