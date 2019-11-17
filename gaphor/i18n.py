"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.

"""
__all__ = ["gettext"]

import gettext as _gettext
import os

import importlib_metadata

localedir = os.path.join(
    importlib_metadata.distribution("gaphor").locate_file("gaphor/data/locale")
)

try:

    catalog = _gettext.Catalog("gaphor", localedir=localedir)
    gettext = catalog.gettext

except OSError:

    def gettext(s):
        return s
