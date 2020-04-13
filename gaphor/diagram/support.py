"""
For ease of creation, maintain a mapping from Element to Diagram Item.
"""

from typing import Dict

from gaphor.core.modeling import Element, Presentation


def represents(uml_element):
    """
    A decorator to assign a default Element type to a diagram item.
    """

    def wrapper(presentation):
        set_diagram_item(uml_element, presentation)
        return presentation

    return wrapper


# Map elements to their (default) representation.
_element_to_item_map: Dict[Element, Presentation] = {}


def get_diagram_item(element):
    global _element_to_item_map
    return _element_to_item_map.get(element)


def set_diagram_item(element, item):
    global _element_to_item_map
    _element_to_item_map[element] = item
