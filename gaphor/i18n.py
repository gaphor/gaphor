"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the translate() function.

"""
__all__ = ["translate"]

import gettext
import os

import importlib_metadata

localedir = os.path.join(
    importlib_metadata.distribution("gaphor").locate_file("gaphor/data/locale")
)

try:

    catalog = gettext.Catalog("gaphor", localedir=localedir)
    translate = catalog.gettext

except OSError:

    def translate(s):
        return s
