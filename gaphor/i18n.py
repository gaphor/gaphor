"""Internationalization (i18n) support for Gaphor.

Translate text in to your native language using the gettext() function.
"""
__all__ = ["gettext"]

import functools
import gettext as _gettext
import importlib.resources
import logging
import xml.etree.ElementTree as etree

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


@functools.lru_cache(maxsize=None)
def translated_ui_string(package: str, ui_filename: str) -> str:
    with importlib.resources.path(package, ui_filename) as ui_path:
        ui_xml = etree.parse(ui_path)
    for node in ui_xml.findall(".//*[@translatable='yes']"):
        node.text = gettext(node.text or "")
        del node.attrib["translatable"]
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")
