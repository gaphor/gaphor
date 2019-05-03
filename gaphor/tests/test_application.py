"""Application service test cases."""

import unittest

from gaphor import UML
from gaphor.application import Application
from gaphor.interfaces import IService


class LoadServiceTestCase(unittest.TestCase):

    """Test case for loading Gaphor services."""

    def test_service_load(self):
        """Test loading services and querying utilities."""

        Application.init(["undo_manager", "file_manager", "properties"])

        self.assertTrue(
            Application.get_service("undo_manager") is not None,
            "Failed to load the undo manager service",
        )

        self.assertTrue(
            Application.get_service("file_manager") is not None,
            "Failed to load the file manager service",
        )

        Application.shutdown()
