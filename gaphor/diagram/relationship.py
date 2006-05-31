'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4:et

import gobject
import diacanvas
from gaphor import UML
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

        # First check if the right subject is already connected:
        if self.subject and \
           getattr(self.subject, edge_head_name) is head_subject and \
           getattr(self.subject, edge_tail_name) is tail_subject:
            return self.subject

        # This is the type of the relationship we're looking for
        required_type = getattr(type(tail_subject), node_tail_name).type

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, node_tail_name):
            if not isinstance(gen, required_type):
                continue
                
            gen_head = getattr(gen, edge_head_name)
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

