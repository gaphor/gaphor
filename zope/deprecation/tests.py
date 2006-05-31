##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Component Architecture Tests

$Id$
"""
import sys
import unittest
import warnings
from zope.testing import doctest

# Used in doctests
from deprecation import deprecated
demo1 = 1
deprecated('demo1', 'demo1 is no more.')

demo2 = 2
deprecated('demo2', 'demo2 is no more.')

demo3 = 3
deprecated('demo3', 'demo3 is no more.')


orig_showwarning = warnings.showwarning

def showwarning(message, category, filename, lineno, file=None):
    sys.stdout.write("From tests.py's showwarning():\n")
    sys.stdout.write(
        warnings.formatwarning(message, category, filename, lineno))

def setUp(test):
    warnings.showwarning = showwarning

def tearDown(test):
    warnings.showwarning = orig_showwarning

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
