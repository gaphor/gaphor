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


#class Relationship(object):
#    """Help! What does this class do?
#    """
#
#    def __init__(self, head_a = None, head_b = None, tail_a = None, tail_b = None):
#        super(Relationship, self).__init__()
#        self.head_relation = head_a, head_b
#        self.tail_relation = tail_a, tail_b
#
#    # python descriptor protol
#    def __get__(self, line, cls):
#        if not line:
#            return self
#
#        return self.relationship(line)
#        
#    def __set__(self, line, value):
#        pass
#
#    def __delete__(self, line):
#        pass
#
#    def relationship(self, line, head_subject = None, tail_subject = None):
#        return self.find(line, self.head_relation, self.tail_relation,
#                head_subject, tail_subject)
#
#    def find(self, line, head_relation, tail_relation,
#            head_subject = None, tail_subject = None):
#        """
#        Figure out what elements are used in a relationship.
#        """
#
#        if not head_subject and not tail_subject:
#            head_subject = line.head.connected_to.subject
#            tail_subject = line.tail.connected_to.subject
#
#        edge_head_name = head_relation[0]
#        node_head_name = head_relation[1]
#        edge_tail_name = tail_relation[0]
#        node_tail_name = tail_relation[1]
#
#        # First check if the right subject is already connected:
#        if line.subject \
#                and getattr(line.subject, edge_head_name) is head_subject \
#                and getattr(line.subject, edge_tail_name) is tail_subject:
#            return line.subject
#
#        # This is the type of the relationship we're looking for
#        required_type = getattr(type(tail_subject), node_tail_name).type
#
#        # Try to find a relationship, that is already created, but not
#        # yet displayed in the diagram.
#        for gen in getattr(tail_subject, node_tail_name):
#            if not isinstance(gen, required_type):
#                continue
#                
#            gen_head = getattr(gen, edge_head_name)
#            try:
#                if not head_subject in gen_head:
#                    continue
#            except TypeError:
#                if not gen_head is head_subject:
#                    continue
#
#            # check for this entry on line.canvas
#            for item in gen.presentation:
#                # Allow line to be returned. Avoids strange
#                # behaviour during loading
#                if item.canvas is line.canvas and item is not line:
#                    break
#            else:
#                return gen
#        return None


class DiagramItemMeta(type):
    """Initialize a new diagram item.
    1. Register UML.Elements by means of the __uml__ attribute (see
       mapUMLClass method).
    1. Set items styles information.

    styles - style information
    """

    def __init__(self, name, bases, data):
#        cls = type.__new__(self, name, bases, data)
        type.__init__(self, name, bases, data)

        self.mapUMLClass(data)
        self.setStyles(bases, data)

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


    def setStyles(self, bases, data):
        """
        Set item styles information by merging provided information with
        style information from base classes.

        cls   - new instance of diagram item class
        bases - base classes of an item
        data  - metaclass data with styles information
        """
        styles = Styles()
        for c in bases:
            if hasattr(c, 'styles'):
                for (name, value) in c.styles.items():
                    styles.add(name, value)

        if '__style__' in data:
            for (name, value) in data['__style__'].iteritems():
                styles.add(name, value)

        self.styles = styles




#class LineItemMeta(DiagramItemMeta):
#    """Add support for __relationship__ (what does it do?) 
#    """
#    def __new__(cls, name, bases, data):
#        item_class = DiagramItemMeta.__new__(cls, name, bases, data)
#
#        # set line relationship
#        if '__relationship__' in data:
#            rel = data['__relationship__']
#            if isinstance(rel, (tuple, set, list)):
#                rel = Relationship(*rel)
#                item_class.relationship = rel
#
#        # set head and tail handles
#
#        return item_class


#if __debug__: 
#    # Keep track of all model elements that are created
#    from gaphor.misc.aspects import ReferenceAspect, weave_method
#    from gaphor import refs
#    weave_method(create_as, ReferenceAspect, refs)

# vim:sw=4:et
