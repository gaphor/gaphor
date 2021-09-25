"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.
"""
__all__ = ["gettext"]

import gettext as _gettext
import importlib.resources
import logging

log = logging.getLogger(__name__)

try:
    with importlib.resources.path("gaphor", "__init__.py") as path:
        localedir = path.parent / "locale"
        translate = _gettext.translation("gaphor", localedir=localedir, fallback=True)
        gettext = translate.gettext

except OSError as e:
    log.warning(f"No translations were found: {e}")

    def gettext(s):
        return s
