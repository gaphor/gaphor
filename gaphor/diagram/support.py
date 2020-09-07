"""For ease of creation, maintain a mapping from Element to Diagram Item."""

from typing import Dict

from gaphor.core.modeling import Element, Presentation


def represents(uml_element):
    """A decorator to assign a default Element type to a diagram item."""

    def wrapper(presentation):
        set_diagram_item(uml_element, presentation)
        return presentation

    return wrapper


# Map elements to their (default) representation.
_element_to_item_map: Dict[Element, Presentation] = {}


def get_diagram_item(element_cls):
    global _element_to_item_map
    return _element_to_item_map.get(element_cls)


def get_model_element(item_cls):
    global _element_to_item_map
    elements = [
        element
        for element, presentation in _element_to_item_map.items()
        if item_cls is presentation
    ]
    return elements[0] if elements else None


def set_diagram_item(element, item):
    global _element_to_item_map
    _element_to_item_map[element] = item
