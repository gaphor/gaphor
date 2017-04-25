
from __future__ import absolute_import
import doctest
from gaphor import action

def test_suite():
    return doctest.DocTestSuite(action)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')

# vim:sw=4:et:ai
