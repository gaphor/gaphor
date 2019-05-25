"""
For ease of creation, maintain a mapping from UML Element to Diagram Item.
"""


# Map UML elements to their (default) representation.
_uml_to_item_map = {}


def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)


def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item
