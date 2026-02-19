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


def force_english_locale():
    """Force English locale, instead of OS language."""
    global gettext
    gettext = translation("en_US.UTF-8").gettext
    translated_ui_string._current_lang = "en"
    _translated_ui_string_cached.cache_clear()


def set_ui_language(lang: str) -> None:
    """Set the UI language. Use \"\" for system default, \"en\" for English, or a locale code (e.g. \"fr\")."""
    global gettext
    if not lang:
        lang_env = os.getenv("LANG") or _get_os_language()
        gettext = translation(lang_env).gettext
        translated_ui_string._current_lang = lang_env or ""
    elif lang.lower() in ("c", "en", "en_us", "en_us.utf-8"):
        gettext = translation("en_US.UTF-8").gettext
        translated_ui_string._current_lang = "en"
    else:
        gettext = translation(lang).gettext
        translated_ui_string._current_lang = lang
    _translated_ui_string_cached.cache_clear()


def get_available_ui_languages() -> list[tuple[str, str]]:
    """Return list of (locale_code, display_name) for all locales with translations.
    First item is always (\"\", display name for System).
    """
    from babel import Locale

    result: list[tuple[str, str]] = []
    # Translators: label for "use system default language" in preferences
    system_label = gettext("System")
    result.append(("", system_label))
    try:
        for path in localedir.iterdir():
            if not path.is_dir():
                continue
            lc_messages = path / "LC_MESSAGES" / "gaphor.mo"
            if not lc_messages.exists():
                continue
            code = path.name
            try:
                name = Locale.parse(code).get_language_name().title()
            except Exception:
                name = code
            result.append((code, name))
        result.sort(key=lambda x: (x[0] == "", x[1].casefold()))
    except OSError:
        pass
    return result


def _initial_language() -> str:
    return os.getenv("LANG") or _get_os_language() or ""


_initial_lang = _initial_language()
gettext = translation(_initial_lang).gettext


def i18nize(message):
    """Pick up text for internationalization without actually translating it, like gettext() does."""
    return message


def _translated_ui_string_impl(
    package: str, ui_filename: str, lang: str
) -> str:
    """Load UI XML and translate all translatable nodes. Cached per (package, filename, lang)."""
    with (importlib.resources.files(package) / ui_filename).open(
        encoding="utf-8"
    ) as ui_file:
        ui_xml = etree.parse(ui_file)
    # Use the translation for the requested language so menu and all UI use it
    trans = translation(lang or _initial_lang).gettext
    for node in ui_xml.findall(".//*[@translatable='yes']"):
        node.text = trans(node.text) if node.text else ""
        del node.attrib["translatable"]
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")  # type: ignore[no-any-return]


_translated_ui_string_cached = functools.lru_cache(maxsize=None)(
    _translated_ui_string_impl
)


def translated_ui_string(package: str, ui_filename: str) -> str:
    """Return UI XML string with all translatable strings in the current UI language.
    Used for menu, preferences, and all .ui files so they are internationalized.
    """
    lang = getattr(translated_ui_string, "_current_lang", None)
    if lang is None:
        translated_ui_string._current_lang = _initial_lang
        lang = _initial_lang
    return _translated_ui_string_cached(package, ui_filename, lang)
