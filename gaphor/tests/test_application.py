"""Unittest the storage and parser modules
"""

import os
import testcase
from gaphor import UML
from gaphor.application import Application
from zope import component
from gaphor.interfaces import IService


class StorageTestCase(testcase.TestCase):

    services = ['undo_manager', 'file_manager']

    def test_service(self):
        """
        Load services. At lease the undo_manager should be available after that.
        """
        
        assert Application.get_service('undo_manager')
        assert Application.get_service('file_manager')

        # After that, services are also available as Utilities:
        assert component.queryUtility(IService, 'undo_manager')
        assert component.queryUtility(IService, 'file_manager')


# vim:sw=4:et:ai
