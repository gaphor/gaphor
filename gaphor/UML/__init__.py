from collection import collection
from uml2 import *
from elementfactory import ElementFactory

# Make one ElementFactory instance an application-wide resource

import gaphor
_default_element_factory = gaphor.resource(ElementFactory)
del gaphor

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

if 0 and __debug__: 
    # Keep track of all model elements that are created
    from gaphor.misc.aspects import ReferenceAspect, LoggerAspect, weave_method
    import elementfactory
    import diagram
    from gaphor import refs
    weave_method(elementfactory.ElementFactory.create_as, ReferenceAspect, refs)
    weave_method(diagram.Diagram.create, ReferenceAspect, refs)
    #weave_method(Element.notify, LoggerAspect)
