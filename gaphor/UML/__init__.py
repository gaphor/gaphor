from collection import collection
from uml2 import *
from elementfactory import ElementFactory

if __debug__: 
    # Keep track of all model elements that are created
    from gaphor.misc.aspects import ReferenceAspect, weave_method
    import elementfactory
    import diagram
    from gaphor import refs
    weave_method(elementfactory.ElementFactory.create_as, ReferenceAspect, refs)
    weave_method(diagram.Diagram.create, ReferenceAspect, refs)
