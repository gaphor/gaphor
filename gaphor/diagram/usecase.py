'''
Use case diagram item
'''
# vim:sw=4

from __future__ import generators

import diacanvas
from gaphor import UML
from nameditem import SimpleNamedItem

class UseCaseItem(SimpleNamedItem):
    __uml__ = UML.UseCase

    def get_border(self):
        return diacanvas.shape.Ellipse()

    def draw_border(self):
        self._border.ellipse(center=(self.width / 2, self.height / 2),
                              width=self.width, height=self.height)


