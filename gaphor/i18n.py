# vim:sw=4:et
"""Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language.
"""

# default locale dir = sys.prefix/share/locale/<lang>/LC_MESSAGES/gaphor.mo

__all__ = [ '_' ]

import gettext

try:
    catalog = gettext.Catalog('gaphor')
    _ = catalog.gettext
except IOError:
    def _(s): return s

