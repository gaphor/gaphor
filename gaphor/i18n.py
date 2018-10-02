"""Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language."""

__all__ = [ '_' ]

import os

import gettext
import pkg_resources

localedir = os.path.join(pkg_resources.get_distribution('gaphor').location, \
                         'gaphor', 'data', 'locale')

try:
    
    catalog = gettext.Catalog('gaphor', localedir=localedir)
    _ = catalog.gettext
    
except IOError, e:
    
    def _(s): return s

