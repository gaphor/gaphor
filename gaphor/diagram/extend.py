'''
Dependency -- 
'''
# vim:sw=4:et

from __future__ import generators

import math
import gobject
import pango
import diacanvas
import gaphor
from gaphor import UML

from include import IncludeItem, STEREOTYPE_OPEN, STEREOTYPE_CLOSE


class ExtendItem(IncludeItem):
    """A UseCase Include dependency.
    """

    __uml__ = UML.Extend

    FONT = 'sans 10'

    def __init__(self, id=None):
        IncludeItem.__init__(self, id)

        self._stereotype.set_text(STEREOTYPE_OPEN + 'extend' + STEREOTYPE_CLOSE)

    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        return self._find_relationship(head_subject, tail_subject,
                                       ('extendedCase', None),
                                       ('extension', 'extend'))

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().

        In case of an Implementation, the head should be connected to an
        Interface and the tail to a BehavioredClassifier.

        TODO: Should Class also inherit from BehavioredClassifier?
        """
        #print 'confirm_connect_handle', handle, self.subject
        c1 = self.handles[0].connected_to

        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                relation = UML.create(UML.Extend)
                relation.extendedCase = s1
                relation.extension = s2
            self.subject = relation
