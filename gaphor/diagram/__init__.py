"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

__version__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

import inspect
import gobject

from gaphor.misc import uniqueid
from gaphor.diagram.align import ItemAlign

# Map UML elements to their (default) representation.
_uml_to_item_map = { }

def create(type):
    return create_as(type, uniqueid.generate_id())

def create_as(type, id):
    return type(id)

def get_diagram_item(element):
    global _uml_to_item_map
    return _uml_to_item_map.get(element)

def set_diagram_item(element, item):
    global _uml_to_item_map
    _uml_to_item_map[element] = item



class Styles(object):
    """
    Item style information. Style information is provided through object's
    attributes, i.e.

        __style__ = {
            'name-align': ('center', 'top'),
        }

    is translated to

        >>> print style.name_align
        ('center', 'top')
    """
    def add(self, name, value):
        """
        Add style variable.

        Variable name can contain hyphens, which is converted to
        underscode, i.e. 'name-align' -> 'name_align'.

        name  - style variable name
        value - style variable value
        """
        name = name.replace('-', '_')
        setattr(self, name, value)


    def items(self):
        """
        Return iterator of (name, value) style information items.
        """
        return self.__dict__.iteritems()



class DiagramItemMeta(type):
    """Initialize a new diagram item.
    1. Register UML.Elements by means of the __uml__ attribute (see
       mapUMLClass method).
    1. Set items styles information.

    styles - style information
    """

    def __init__(self, name, bases, data):
        type.__init__(self, name, bases, data)

        self.mapUMLClass(data)
        self.setStyles(data)


    def mapUMLClass(self, data):
        """
        Map UML class to diagram item.

        cls  - new instance of item class
        data - metaclass data with UML class information 

        """
        if '__uml__' in data:
            obj = data['__uml__']
            if isinstance(obj, (tuple, set, list)):
                for c in obj:
                    set_diagram_item(c, self)
            else:
                set_diagram_item(obj, self)


    def setStyles(self, data):
        """
        Set item styles information by merging provided information with
        style information from base classes.

        cls   - new instance of diagram item class
        bases - base classes of an item
        data  - metaclass data with styles information
        """
        styles = Styles()
        for c in self.__bases__:
            if hasattr(c, 'styles'):
                for (name, value) in c.styles.items():
                    styles.add(name, value)

        if '__style__' in data:
            for (name, value) in data['__style__'].iteritems():
                styles.add(name, value)

        self.styles = styles

# vim:sw=4:et
