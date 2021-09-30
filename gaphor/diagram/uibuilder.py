import functools
import importlib.resources
import xml.etree.ElementTree as etree

from gaphor.i18n import gettext


@functools.lru_cache(maxsize=None)
def translated_ui_string(package: str, ui_filename: str) -> str:
    with importlib.resources.path(package, ui_filename) as ui_path:
        ui_xml = etree.parse(ui_path)
    for node in ui_xml.findall(".//*[@translatable='yes']"):
        node.text = gettext(node.text or "")
        del node.attrib["translatable"]
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")
