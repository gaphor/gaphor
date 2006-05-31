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
"""Placeless Test Setup

$Id$
"""
from zope.testing import cleanup

# A mix-in class inheriting from CleanUp that also connects the CA services
class PlacelessSetup(cleanup.CleanUp):

    def setUp(self):
        super(PlacelessSetup, self).setUp()

    def tearDown(self):
        super(PlacelessSetup, self).tearDown()


def setUp(test=None):
    cleanup.setUp()

def tearDown(test=None):
    cleanup.tearDown()
