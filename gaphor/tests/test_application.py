"""
Service test cases.
"""

from gaphor.tests.testcase import TestCase
from gaphor import UML
from gaphor.application import Application
from zope import component
from gaphor.interfaces import IService


class ServiceTestCase(TestCase):

    services = ['undo_manager', 'file_manager']

    def test_service(self):
        """
        Load services. At lease the undo_manager should be available after that.
        """
        self.assertTrue(Application.get_service('undo_manager') is not None)
        self.assertTrue(Application.get_service('file_manager') is not None)

        # After that, services are also available as Utilities:
        self.assertTrue(component.queryUtility(IService, 'undo_manager') is not None)
        self.assertTrue(component.queryUtility(IService, 'file_manager') is not None)


# vim:sw=4:et:ai
