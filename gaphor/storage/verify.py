"""
Verify the content of an element factory before it is saved.


"""

from __future__ import absolute_import

import gaphas

from gaphor.UML import uml2
from gaphor.UML.collection import collection


def orphan_references(factory):
    """
    Verify the contents of the element factory. Only checks are done
    that ensure the model can be loaded back again.

    TODO: Okay, now I can predict if a model can be loaded after it's
    saved, but I have no means to correct or fix the model.
    """

    # Maintain a set of id's, one for elements, one for references.
    # Write only to file if references is a subset of elements

    refs = set()
    elements = set()

    def verify_reference(name, value):
        """
        Store the reference
        """
        # Save a reference to the object:
        if value.id:
            refs.add((value.id, value))

    def verify_collection(name, value):
        """
        Store a list of references.
        """
        for v in value:
            if v.id:
                refs.add((v.id, v))

    def verify_element(name, value):
        """
        Store the element id.
        """
        if isinstance(value, (uml2.Element, gaphas.Item)):
            verify_reference(name, value)
        elif isinstance(value, collection):
            verify_collection(name, value)
        elif isinstance(value, gaphas.Canvas):
            value.save(verify_canvasitem)

    def verify_canvasitem(name, value, reference=False):
        """
        Verify attributes and references in a gaphor.diagram.* object.
        The extra attribute reference can be used to force UML 
        """
        # log.debug('saving canvasitem: %s|%s %s' % (name, value, type(value)))
        if isinstance(value, collection) or \
                (isinstance(value, (list, tuple)) and reference == True):
            verify_collection(name, value)
        elif reference:
            verify_reference(name, value)
        elif isinstance(value, gaphas.Item):
            elements.add(value.id)
            value.save(verify_canvasitem)

            # save subitems
            for child in value.canvas.get_children(value):
                verify_canvasitem(None, child)

        elif isinstance(value, uml2.Element):
            verify_reference(name, value)

    for e in factory.values():
        assert e.id
        elements.add(e.id)
        e.save(verify_element)

    return [r[1] for r in refs if not r[0] in elements]

# vim:sw=4:et:ai
