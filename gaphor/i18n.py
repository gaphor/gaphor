# vim:sw=4:et
"""
Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language.
"""

__all__ = [ '_' ]

import os

import gettext
import pkg_resources

# default locale dir = site-base/gaphor/data/locale/<lang>/LC_MESSAGES/gaphor.mo
localedir = os.path.join(pkg_resources.get_distribution('gaphor').location, \
                         'gaphor', 'data', 'locale')

try:
    catalog = gettext.Catalog('gaphor', localedir=localedir)
    #log.info('catalog = %s' % catalog.info())
    _ = catalog.gettext
except IOError, e:
    #log.error('Could not load locale catalog', exc_info=True)
    def _(s): return s

