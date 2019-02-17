"""
Action diagram item.
"""
from __future__ import division

from past.utils import old_div
from math import pi

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE


class ActionItem(NamedItem):
    __uml__ = UML.Action
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def draw(self, context):
        """
        Draw action symbol.
        """
        super(ActionItem, self).draw(context)

        c = context.cairo

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


class SendSignalActionItem(NamedItem):
    __uml__ = UML.SendSignalAction
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def draw(self, context):
        """
        Draw action symbol.
        """
        super(SendSignalActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w - d, 0)
        c.line_to(w, old_div(h, 2))
        c.line_to(w - d, h)
        c.line_to(0, h)
        c.close_path()

        c.stroke()


class AcceptEventActionItem(NamedItem):
    __uml__ = UML.SendSignalAction
    __style__ = {"min-size": (50, 30), "name-align": (ALIGN_CENTER, ALIGN_MIDDLE)}

    def draw(self, context):
        """
        Draw action symbol.
        """
        super(AcceptEventActionItem, self).draw(context)

        c = context.cairo

        d = 15
        w = self.width
        h = self.height
        c.move_to(0, 0)
        c.line_to(w, 0)
        c.line_to(w, h)
        c.line_to(0, h)
        c.line_to(d, old_div(h, 2))
        c.close_path()

        c.stroke()
