"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

from builtins import str
import inspect
import gi
gi.require_version('PangoCairo', '1.0')

from gi.repository import GObject
import uuid

from gaphor.diagram.style import Style

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, str(uuid.uuid1()))

def create_as(type, id):
    return type(id)

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



class DiagramItemMeta(type):
    """
    Initialize a new diagram item.
    1. Register UML.Elements by means of the __uml__ attribute (see
       map_uml_class method).
    2. Set items style information.

    @ivar style: style information
    """

    def __init__(self, name, bases, data):
        type.__init__(self, name, bases, data)

        self.map_uml_class(data)
        self.set_style(data)


    def map_uml_class(self, data):
        """
        Map UML class to diagram item.

        @param cls:  new instance of item class
        @param data: metaclass data with UML class information

        """
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, self)
            else:
                set_diagram_item(obj, self)


    def set_style(self, data):
        """
        Set item style information by merging provided information with
        style information from base classes.

        @param cls:   new instance of diagram item class
        @param bases: base classes of an item
        @param data:  metaclass data with style information
        """
        style = Style()
        for c in self.__bases__:
            if hasattr(c, 'style'):
                for (name, value) in list(c.style.items()):
                    style.add(name, value)

        if '__style__' in data:
            for (name, value) in data['__style__'].items():
                style.add(name, value)

        self.style = style


# vim:sw=4:et
