"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.
"""
from __future__ import annotations

import functools
import gettext as _gettext
import importlib.resources
import locale
import logging
import os
import sys

import defusedxml.ElementTree as etree

from gaphor.settings import settings

log = logging.getLogger(__name__)

localedir = importlib.resources.files("gaphor") / "locale"


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


@functools.lru_cache(maxsize=2)
def translation(lang) -> _gettext.GNUTranslations | _gettext.NullTranslations:
    try:
        return _gettext.translation(
            "gaphor", localedir=str(localedir), languages=[lang, "C"]
        )
    except FileNotFoundError as e:
        if lang.lower() not in ("c", "c.utf-8", "en_us", "en_us.utf-8"):
            log.warning(f"No translations were found for language {lang}: {e}")
    return _gettext.NullTranslations()


if settings.use_english:
    gettext = translation("en_US.UTF-8").gettext
else:
    gettext = translation(os.getenv("LANG") or _get_os_language()).gettext


def i18nize(message):
    """Pick up text for internationalization without actually translating it, like gettext() does."""
    return message


@functools.cache
def translated_ui_string(package: str, ui_filename: str) -> str:
    with (importlib.resources.files(package) / ui_filename).open(
        encoding="utf-8"
    ) as ui_file:
        ui_xml = etree.parse(ui_file)
    for node in ui_xml.findall(".//*[@translatable='yes']"):
        node.text = gettext(node.text) if node.text else ""
        del node.attrib["translatable"]
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")  # type: ignore[no-any-return]
