"""Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language."""

__all__ = ["_"]

import os

import gettext
import importlib_metadata

localedir = os.path.join(
    importlib_metadata.distribution("gaphor").locate_file("gaphor/data/locale")
)

try:

    catalog = gettext.Catalog("gaphor", localedir=localedir)
    _ = catalog.gettext

except IOError as e:

    def _(s):
        return s
