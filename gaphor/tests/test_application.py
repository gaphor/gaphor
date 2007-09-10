"""
Application service test cases.
"""

import unittest

from gaphor import UML
from gaphor.application import Application
from zope import component
from gaphor.interfaces import IService


class LoadServiceTestCase(unittest.TestCase):
    def test_service_load(self):
        """
        Load services. At lease the undo_manager should be available after that.
        """
        Application.init(['undo_manager', 'file_manager', 'properties'])

        self.assertTrue(Application.get_service('undo_manager') is not None)
        self.assertTrue(Application.get_service('file_manager') is not None)

        # After that, services are also available as Utilities:
        self.assertTrue(component.queryUtility(IService, 'undo_manager') is not None)
        self.assertTrue(component.queryUtility(IService, 'file_manager') is not None)

        Application.shutdown()


# vim:sw=4:et:ai
