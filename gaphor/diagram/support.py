"""
For ease of creation, maintain a mapping from UML Element to Diagram Item.
"""

from typing import Dict

from gaphor import UML
from gaphor.core.modeling import Presentation


def represents(uml_element):
    """
    A decorator to assign a default UML Element type to a diagram item.
    """

    def wrapper(presentation):
        set_diagram_item(uml_element, presentation)
        return presentation

    return wrapper


# Map UML elements to their (default) representation.
_uml_to_item_map: Dict[UML.Element, Presentation] = {}


def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)


def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item
