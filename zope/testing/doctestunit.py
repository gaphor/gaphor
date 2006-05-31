##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Extension to use doctest tests as unit tests

This module provides a DocTestSuite contructor for converting doctest
tests to unit tests.

$Id$
"""

from doctest import DocFileSuite, DocTestSuite
from doctest import debug_src, debug

def pprint():
    from pprint import PrettyPrinter
    def pprint(ob, **opts):
        if 'width' not in opts:
            opts['width'] = 1
        return PrettyPrinter(**opts).pprint(ob)
    return pprint

pprint = pprint()
