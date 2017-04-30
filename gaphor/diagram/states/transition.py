"""
State transition implementation.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.core import inject
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_RIGHT, ALIGN_TOP


class TransitionItem(NamedLine):
    """
    Representation of state transition.
    """
    __uml__ = uml2.Transition

    __style__ = {
        'name-align': (ALIGN_RIGHT, ALIGN_TOP),
        'name-padding': (5, 15, 5, 5),
    }

    element_factory = inject('element_factory')

    def __init__(self, id=None):
        NamedLine.__init__(self, id)
        self._guard = self.add_text('guard.specification', editable=True)
        self.watch('subject<Transition>.guard<Constraint>.specification', self.on_guard)

    def postload(self):
        """
        Load guard specification information.
        """
        try:
            self._guard.text = self.subject.guard.specification or ''
        except AttributeError:
            self._guard.text = ''
        super(TransitionItem, self).postload()

    def on_guard(self, event):
        try:
            self._guard.text = self.subject.guard.specification or ''
        except AttributeError:
            self._guard.text = ''
        self.request_update()

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)

# vim:sw=4:et:ai
