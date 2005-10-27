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
"""ITracebackSupplement interface definition.

$Id$
"""


from zope.interface import Interface, Attribute

class ITracebackSupplement(Interface):
    """Provides valuable information to supplement an exception traceback.

    The interface is geared toward providing meaningful feedback when
    exceptions occur in user code written in mini-languages like
    Zope page templates and restricted Python scripts.
    """

    source_url = Attribute(
        'source_url',
        """Optional.  Set to URL of the script where the exception occurred.

        Normally this generates a URL in the traceback that the user
        can visit to manage the object.  Set to None if unknown or
        not available.
        """
        )

    line = Attribute(
        'line',
        """Optional.  Set to the line number (>=1) where the exception
        occurred.

        Set to 0 or None if the line number is unknown.
        """
        )

    column = Attribute(
        'column',
        """Optional.  Set to the column offset (>=0) where the exception
        occurred.

        Set to None if the column number is unknown.
        """
        )

    expression = Attribute(
        'expression',
        """Optional.  Set to the expression that was being evaluated.

        Set to None if not available or not applicable.
        """
        )

    warnings = Attribute(
        'warnings',
        """Optional.  Set to a sequence of warning messages.

        Set to None if not available, not applicable, or if the exception
        itself provides enough information.
        """
        )


    def getInfo(as_html=0):
        """Optional.  Returns a string containing any other useful info.

        If as_html is set, the implementation must HTML-quote the result
        (normally using cgi.escape()).  Returns None to provide no
        extra info.
        """
