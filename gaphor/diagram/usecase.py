"""
Use case diagram item.
"""
from __future__ import division

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE
from gaphor.diagram.textelement import text_extents


class UseCaseItem(ClassifierItem):
    """
    Presentation of gaphor.UML.UseCase.
    """

    __uml__ = UML.UseCase
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def __init__(self, id=None):
        super(UseCaseItem, self).__init__(id)
        self.drawing_style = -1

    def pre_update(self, context):
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = width + 10, height + 20
        super(UseCaseItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo

        rx = self.width / 2.0
        ry = self.height / 2.0

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        cr.stroke()

        super(UseCaseItem, self).draw(context)


# vim:sw=4:et
