"""
State transition implementation.
"""

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP


class TransitionItem(NamedLine):
    """
    Representation of state transition.
    """

    __uml__ = UML.Transition

    __style__ = {
            'name-align': (ALIGN_RIGHT, ALIGN_TOP),
            'name-padding': (5, 15, 5, 5),
    }

    def __init__(self, id = None):
        NamedLine.__init__(self, id)
        self._guard = self.add_text('guard.specification.value', editable=True)
        self.add_watch(UML.Transition.guard, self.on_guard)
        self.add_watch(UML.Constraint.specification, self.on_guard)
        self.add_watch(UML.LiteralSpecification.value, self.on_guard)


    def postload(self):
        """
        Load guard specification information.
        """
        if self.subject and self.subject.guard:
            self._guard.text = self.subject.guard.specification.value
        super(TransitionItem, self).postload()


    def on_guard(self, event):
        if not self.subject:
            return
        element = event.element
        guard = self.subject.guard
        if event is None or \
                (element is self.subject) or \
                (element is guard) or \
                (guard and element is guard.specification):
            try:
                self._guard.text = self.subject.guard.specification.value or ''
            except AttributeError:
                # Have a no-value here
                self._guard.text = ''
            self.request_update()


    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


    def set_guard(self, value):
        self.subject.guard.specification.value = value
        self._guard.text = value


# vim:sw=4:et:ai
