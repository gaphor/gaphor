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
"""General exceptions that wish they were standard exceptions

These exceptions are so general purpose that they don't belong in Zope
application-specific packages.

$Id$
"""

import zope.deprecation

zope.deprecation.deprecated('INotFoundError',
                            'This interface has been deprecated. '
                            'Use standard interface instead '
                            'The reference will be gone in 3.3')

zope.deprecation.deprecated('NotFoundError',
                            'This class has been deprecated. '
                            'Use standard exceptions instead '
                            'The reference will be gone in 3.3')

# Turn of deprecation warning here for the above import that are here for BBB
# The depreaction above and within the _notfounderror module will do the job.
zope.deprecation.__show__.off()
from zope.exceptions._notfounderror import NotFoundError, INotFoundError
zope.deprecation.__show__.on()

from zope.exceptions._duplicate import DuplicationError, IDuplicationError

# Importing these interfaces from here is deprecated!

# avoid depency on zope.security:
try:
    import zope.security
except ImportError, v:
    # "ImportError: No module named security"
    if not str(v).endswith(' security'):
        raise
else:
    from zope.security.interfaces import IUnauthorized, Unauthorized
    from zope.security.interfaces import IForbidden, IForbiddenAttribute
    from zope.security.interfaces import Forbidden, ForbiddenAttribute
