"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.
"""
from __future__ import annotations

__all__ = ["gettext"]

import functools
import gettext as _gettext
import importlib.resources
import locale
import logging
import os
import sys
import xml.etree.ElementTree as etree

log = logging.getLogger(__name__)


def _get_os_language() -> str:
    """Get the default language in Windows or macOS.

    Inspired by https://github.com/nicotine-plus/nicotine-plus
    locale.getlocale() fails to get the correct language if the region
    is set different from the language.
    """
    if sys.platform == "darwin":
        from Cocoa import NSUserDefaults

        defaults = NSUserDefaults.standardUserDefaults()
        langs = defaults.objectForKey_("AppleLanguages")
        if language := langs.objectAtIndex_(0):
            assert isinstance(language, str)
            return language.replace("-", "_")
    elif sys.platform == "win32":
        import ctypes

        windll = ctypes.windll.kernel32
        if language := locale.windows_locale.get(windll.GetUserDefaultUILanguage()):
            return language
    return ""


try:
    if os.getenv("LANG") is None:
        os.environ["LANG"] = _get_os_language()
    localedir = importlib.resources.files("gaphor") / "locale"
    translate = _gettext.translation("gaphor", localedir=str(localedir))
    gettext = translate.gettext

except OSError as e:
    lang = os.getenv("LANG", "")
    if lang.lower() not in ("c", "en_us", "en_us.utf-8"):
        log.warning(f"No translations were found for language {lang}: {e}")

    def gettext(s):
        return s


@functools.lru_cache(maxsize=None)
def translated_ui_string(package: str, ui_filename: str) -> str:
    with (importlib.resources.files(package) / ui_filename).open(
        encoding="utf-8"
    ) as ui_file:
        ui_xml = etree.parse(ui_file)
    for node in ui_xml.findall(".//*[@translatable='yes']"):
        node.text = gettext(node.text) if node.text else ""
        del node.attrib["translatable"]
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")
