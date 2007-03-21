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
from gaphor.diagram.style import Style

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


##
## Direct revert-statements from gaphas to the undomanager
###

from gaphas import state
from gaphor.undomanager import get_undo_manager, transactional

print 'state', state
state.observers.add(state.revert_handler)

def _undo_handler(event):
    get_undo_manager().add_undo_action(lambda: state.saveapply(*event));

state.subscribers.add(_undo_handler)

# vim:sw=4:et
