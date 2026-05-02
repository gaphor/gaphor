from gaphor.core.format import format
from gaphor.KerML import kerml


@format.register(kerml.Element)
def format_kerml_element(el: kerml.Element, **kwargs):
    return el.declaredName or el.elementId or ""
