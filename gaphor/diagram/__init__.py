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



class Style(object):
    """
    Item style information. Style information is provided through object's
    attributes, i.e.::

        class InitialNodeItem
            __style__ = {
                'name-align': ('center', 'top'),
            }

    is translated to::

        >>> print style.name_align
        ('center', 'top')
    """
    def add(self, name, value):
        """
        Add style variable.

        Variable name can contain hyphens, which is converted to
        underscode, i.e. 'name-align' -> 'name_align'.

        @param name:  style variable name
        @param value: style variable value
        """
        name = name.replace('-', '_')
        setattr(self, name, value)


    def items(self):
        """
        Return iterator of (name, value) style information items.
        """
        return self.__dict__.iteritems()



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
                for (name, value) in c.style.items():
                    style.add(name, value)

        if '__style__' in data:
            for (name, value) in data['__style__'].iteritems():
                style.add(name, value)

        self.style = style

# vim:sw=4:et
