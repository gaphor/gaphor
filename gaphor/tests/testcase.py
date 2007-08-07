"""
Basic test case for Gaphor tests.

Everything is about services so the TestCase can define it's required
services and start off.
"""

import unittest
from gaphor.application import Application

# Increment log level
log.set_log_level(log.WARNING)


class TestCase(unittest.TestCase):
    
    services = []
    
    def setUp(self):
        Application.init(services=self.services)

    def tearDown(self):
        Application.shutdown()
        
    def get_service(self, name):
        return Application.get_service(name)

main = unittest.main

# vim:sw=4:et:ai
