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


def uml(uml_class, stereotype=None):
    """
    Assign UML metamodel class and a stereotype to diagram item.

    :Parameters:
     uml_class
        UML metamodel class.
     stereotype
        Stereotype name (i.e. 'subsystem').
    """

    def f(item_class):
        t = uml_class
        if stereotype is not None:
            t = (uml_class, stereotype)
            item_class.__stereotype__ = stereotype
        set_diagram_item(t, item_class)
        return item_class

    return f
