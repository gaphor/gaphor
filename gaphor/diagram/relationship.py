'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4:et

import gobject
import diacanvas
import gaphor.UML as UML
from gaphor.diagram import initialize_item
from diagramline import DiagramLine

# TODO: Relationship should be extended to add a name/stereotype label
# Dependencies -> stereotype,
# Association -> name or stereotype
# Generatization -> stereotype

class RelationshipItem(DiagramLine):
    
    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def save (self, save_func):
        DiagramLine.save(self, save_func)

    def load (self, name, value):
	DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)

    def _find_relationship(self, head_subject, tail_subject,
                           head_relation, tail_relation):
        """Figure out what elements are used in a relationship.
        """
        edge_head_name = head_relation[0]
        node_head_name = head_relation[1]
        edge_tail_name = tail_relation[0]
        node_tail_name = tail_relation[1]

	if self.subject and \
	   getattr(self.subject, head_relation[0]) is head_subject and \
	   getattr(self.subject, tail_relation[0]) is tail_subject:
	    return self.subject

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, tail_relation[1]):
            gen_head = getattr(gen, head_relation[0])
            try:
                if not head_subject in gen_head:
                    continue
            except TypeError:
                if not gen_head is head_subject:
                    continue

            # check for this entry on self.canvas
            for item in gen.presentation:
                # Allow self to be returned. Avoids strange
                # behaviour during loading
                if item.canvas is self.canvas and item is not self:
                    break
            else:
                return gen
        return None

initialize_item(RelationshipItem)
