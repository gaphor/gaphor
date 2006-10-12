'''
ActionItem diagram item
'''

from math import pi

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphas.util import text_align, text_extents

class ActionItem(NamedItem):
    __uml__      = UML.Action
#    __s_valign__ = V_ALIGN_MIDDLE

    def __init__(self, id):
        super(ActionItem, self).__init__(id)
        self.min_width = 50
        self.min_height = 30
        self.width = self.min_width
        self.height = self.min_height
        self.drawing_style = -1

    def pre_update(self, context):
        cr = context.cairo
        text = self.subject.name
        if text:
            width, height = text_extents(cr, text)
            self.min_width, self.min_height = width + 10, height + 20
        super(ActionItem, self).pre_update(context)

    def draw(self, context):
        c = context.cairo

        rx = self.width / 2.0
        ry = self.height / 2.0

        d = 15

        c.move_to(0, d)
        c.arc(d, d, d, pi, 1.5 * pi)
        c.line_to(self.width - d, 0)
        c.arc(self.width - d, d, d, 1.5 * pi, 0)
        c.line_to(self.width, self.height - d)
        c.arc(self.width - d, self.height - d, d, 0, 0.5 * pi)
        c.line_to(d, self.height)
        c.arc(d, self.height - d, d, 0.5 * pi, pi)
        c.close_path()

        c.stroke()

        text = self.subject.name
        if text:
            text_align(c, rx, ry, text, align_x=0)



# vim:sw=4:et
