'''
Use case diagram item
'''
# vim:sw=4

from __future__ import generators

import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from nameditem import SimpleNamedItem

class UseCaseItem(SimpleNamedItem):

    def get_border(self):
        return diacanvas.shape.Ellipse()

    def draw_border(self):
        self._border.ellipse(center=(self.width / 2, self.height / 2),
                              width=self.width, height=self.height)


initialize_item(UseCaseItem, UML.UseCase)
