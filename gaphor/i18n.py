"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.

"""
__all__ = ["gettext"]

import gettext as _gettext
import importlib.resources
import logging
import os

import importlib_metadata

log = logging.getLogger(__name__)

try:

    with importlib.resources.path("gaphor", "locale") as path:
        translate = _gettext.translation("gaphor", localedir=str(path), fallback=True)
        gettext = translate.gettext

except OSError as e:
    log.info(f"No translations were found: {e}")

    def gettext(s):
        return s
