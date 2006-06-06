"""
Use case inclusion relationship.
"""

from gaphor import resource
from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class IncludeItem(DiagramLine):
    """
    Use case inclusion relationship.
    """

    __uml__ = UML.Include
    __relationship__ = 'addition', None, 'includingCase', 'include'
    __stereotype__ = 'include'

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)
        self.set(head_fill_color=0, head_a=0.0, head_b=15.0, head_c=6.0, head_d=6.0)
        self.set(dash=(7.0, 5.0), has_head=1)

    #
    # Gaphor Connection Protocol
    #

    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.UseCase)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See DiagramLine.confirm_connect_handle().

        TODO: Should Class also inherit from BehavioredClassifier?
        """
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.relationship
            if not relation:
                relation = resource(UML.ElementFactory).create(self.__uml__)

                # in case of Include: set addition and includingCase attributes
                # in case of Extend: set extendedCase and extension attributes
                setattr(relation, self.__relationship__[0], s1)
                setattr(relation, self.__relationship__[3], s2)
            self.subject = relation


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        self.set_subject(None)

# vim:sw=4:et
