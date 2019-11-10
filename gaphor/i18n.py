"""Internationalization (i18n) support for Gaphor.

Here the _() function is defined that is used to translate text into
your native language."""

__all__ = ["_"]

import os

import logging
import gettext
import importlib_metadata
import importlib.resources

log = logging.getLogger(__name__)

try:

    with importlib.resources.path("gaphor", "locale") as path:
        translate = gettext.translation("gaphor", localedir=str(path), fallback=True)
        _ = translate.gettext

except OSError as e:
    log.info(f"No translations were found: {e}")

    def _(s):
        return s
