from gaphor.UML.collection import collection

from gaphor.UML.uml2 import *
from gaphor.UML.elementfactory import ElementFactory

# Make one ElementFactory instance an application-wide resource
from gaphor import resource
_default_element_factory = resource(ElementFactory)
del resource

# Make some elements of the default ElementFactory easely accessable

def create(type):
    """Create a new model element in the default ElementFactory.
    """
    return _default_element_factory.create(type)

def lookup(id):
    """Find the element with id in the default ElementFactory.
    """
    return _default_element_factory.lookup(id)

def select(expression=None):
    """Query the default ElementFactory for items that comply with expression.
    """
    return _default_element_factory.select(expression)

def flush():
    _default_element_factory.flush()

if 0 and __debug__: 
    # Keep track of all model elements that are created
    from gaphor.misc.aspects import ReferenceAspect, LoggerAspect, weave_method
    from gaphor.UML import diagram
    from gaphor import refs
    weave_method(ElementFactory.create_as, ReferenceAspect, refs)
    weave_method(diagram.Diagram.create, ReferenceAspect, refs)
    #weave_method(Element.notify, LoggerAspect)
