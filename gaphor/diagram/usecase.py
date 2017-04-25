"""
Use case diagram item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE
from .textelement import text_extents
from gaphas.util import path_ellipse

class UseCaseItem(ClassifierItem):
    """
    Presentation of gaphor.UML.UseCase.
    """
    __uml__ = uml2.UseCase
    __style__ = {
        'min-size':   (50, 30),
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }

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

        rx = self.width / 2. 
        ry = self.height / 2.

        cr.move_to(self.width, ry)
        path_ellipse(cr, rx, ry, self.width, self.height)
        cr.stroke()

        super(UseCaseItem, self).draw(context)


# vim:sw=4:et
