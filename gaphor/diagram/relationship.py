'''
Relationship -- Base class for dependencies and associations.
'''
# vim:sw=4

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


initialize_item(RelationshipItem)
