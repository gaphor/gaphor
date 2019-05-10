"""
State diagram item.
"""

import operator

from gaphor import UML
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_CENTER, ALIGN_TOP
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.classifier import CompartmentItem
from gaphor.diagram.compartment import FeatureItem
from gaphor.core import inject

DX = 15
DY = 8
DDX = 0.4 * DX
DDY = 0.4 * DY


class VertexItem(NamedItem):
    """
    Abstract class for all vertices. All state, pseudostate items derive
    from VertexItem, which simplifies transition connection adapters.
    """

    pass


class StateItem(CompartmentItem, VertexItem):
    element_factory = inject("element_factory")
    __uml__ = UML.State
    __style__ = {
        "min-size": (50, 30),
        "name-align": (ALIGN_CENTER, ALIGN_TOP),
        "extra-space": "compartment",
    }

    def __init__(self, id):
        super(StateItem, self).__init__(id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self._activities = self.create_compartment("activities")
        self._activities.use_extra_space = True
        # non-visible by default, show when at least one item is visible
        self._activities.visible = False

        self._entry = FeatureItem(pattern="entry / %s", order=1)
        self._exit = FeatureItem(pattern="exit / %s", order=2)
        self._do_activity = FeatureItem(pattern="do / %s", order=3)

    def _set_activity(self, act, attr, text):
        if text and act not in self._activities:
            self._activities.append(act)
            act.subject = self.element_factory.create(UML.Activity)
            act.subject.name = text
            setattr(self.subject, attr, act.subject)

            # sort the activities according to defined order
            self._activities.sort(key=operator.attrgetter("order"))

        elif text and act in self._activities:
            act.subject.name = text
        elif not text and act in self._activities:
            self._activities.remove(act)
            act.subject.unlink()

        self._activities.visible = len(self._activities) > 0
        self.request_update()

    def set_entry(self, text):
        self._set_activity(self._entry, "entry", text)

    def set_exit(self, text):
        self._set_activity(self._exit, "exit", text)

    def set_do_activity(self, text):
        self._set_activity(self._do_activity, "doActivity", text)

    def postload(self):
        super(StateItem, self).postload()
        if self.subject.entry:
            self.set_entry(self.subject.entry.name)
        if self.subject.exit:
            self.set_exit(self.subject.exit.name)
        if self.subject.doActivity:
            self.set_do_activity(self.subject.doActivity.name)

    def draw_compartment_border(self, context):
        """
        Draw state item.
        """
        c = context.cairo

        c.move_to(0, DY)
        c.curve_to(0, DDY, DDX, 0, DX, 0)
        c.line_to(self.width - DX, 0)
        c.curve_to(self.width - DDX, 0, self.width, DDY, self.width, DY)
        c.line_to(self.width, self.height - DY)
        c.curve_to(
            self.width,
            self.height - DDY,
            self.width - DDX,
            self.height,
            self.width - DX,
            self.height,
        )
        c.line_to(DX, self.height)
        c.curve_to(DDX, self.height, 0, self.height - DDY, 0, self.height - DY)
        c.close_path()

        c.stroke()


# vim:sw=4:et
