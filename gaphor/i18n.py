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
    localedir = importlib.resources.files("gaphor") / "locale"
    translate = _gettext.translation("gaphor", localedir=str(localedir), fallback=True)
    gettext = translate.gettext

except OSError as e:
    log.warning(f"No translations were found: {e}")

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
