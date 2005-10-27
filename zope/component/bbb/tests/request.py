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
"""Request for tests

$Id$
"""
import warnings
import zope.interface

from zope.component import bbb

if bbb.tests.__warn__:
    warnings.warn(
        "`zope.component.tests.request` is deprecated, since the component "
        "architecture does not support presentation components anymore.",
        DeprecationWarning, 2)

class Request(object):

    def __init__(self, type, skin=None):
        zope.interface.directlyProvides(self, type)
        # BBB goes away in 3.3
        if skin is not None:
            import warnings
            warnings.warn(
                "The skin argument is deprecated for "
                "zope.component.tests.request.Request and will go away in "
                "Zope 3.3. Use zope.publisher.browser.TestRequest if "
                "you need to test skins.",
                DeprecationWarning)
            zope.interface.directlyProvides(self, skin)
        self._skin = skin
