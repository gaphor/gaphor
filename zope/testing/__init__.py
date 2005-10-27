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
"""Set up testing environment

$Id$
"""
import os

def patchTracebackModule():
    """Use the ExceptionFormatter to show more info in tracebacks.
    """
    from zope.exceptions.exceptionformatter import format_exception
    import traceback
    traceback.format_exception = format_exception

# Don't use the new exception formatter by default, since it
# doesn't show filenames.
if os.environ.get('NEW_ZOPE_EXCEPTION_FORMATTER', 0):
    patchTracebackModule()
