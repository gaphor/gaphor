from gaphor.UML.collection import collection

from gaphor.UML.uml2 import *
from gaphor.UML.elementfactory import ElementFactory


# Make some elements of the default ElementFactory easely accessable

def create(type):
    """Create a new model element in the default ElementFactory.
    """
    from gaphor.application import Application
    return Application.get_service('element_factory').create(type)

def lookup(id):
    """Find the element with id in the default ElementFactory.
    """
    from gaphor.application import Application
    return Application.get_service('element_factory').lookup(id)

def select(expression=None):
    """Query the default ElementFactory for items that comply with expression.
    Returns an iterator.
    """
    from gaphor.application import Application
    return Application.get_service('element_factory').select(expression)

def lselect(expression=None):
    """Query the default ElementFactory for items that comply with expression.
    Returns a list of elements.
    """
    from gaphor.application import Application
    return Application.get_service('element_factory').lselect(expression)

def flush():
    from gaphor.application import Application
    Application.get_service('element_factory').flush()

def swap_element(element, new_class):
    """Swap the class for an element
    """
    from gaphor.application import Application
    Application.get_service('element_factory').swap_element(element, new_class)

if 0 and __debug__: 
    # Keep track of all model elements that are created
    from gaphor.misc.aspects import ReferenceAspect, LoggerAspect, weave_method
    from gaphor.UML import diagram
    from gaphor import refs
    weave_method(ElementFactory.create_as, ReferenceAspect, refs)
    weave_method(diagram.Diagram.create, ReferenceAspect, refs)
    #weave_method(Element.notify, LoggerAspect)
