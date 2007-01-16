"""
ExtensionItem -- Graphical representation of an association.
"""

# TODO: for Extension.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from __future__ import generators

from gaphor import resource
from gaphor import UML
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.diagramline import DiagramLine

class ExtensionItem(DiagramLine):
    """ExtensionItem represents associations. 
    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """

    __uml__ = UML.Extension

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

    def save (self, save_func):
        DiagramLine.save(self, save_func)
        if self._head_end.subject:
            save_func('head_subject', self._head_end.subject)
        if self._tail_end.subject:
            save_func('tail_subject', self._tail_end.subject)

    def load (self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ( 'head_end', 'head_subject' ):
            #type(self._head_end).subject.load(self._head_end, value)
            self._head_end.load('subject', value)
        elif name in ( 'tail_end', 'tail_subject' ):
            #type(self._tail_end).subject.load(self._tail_end, value)
            self._tail_end.load('subject', value)
        else:
            DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)
        self._head_end.postload()
        self._tail_end.postload()

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramLine.on_subject_notify(self, pspec,
                                           notifiers + ('ownedEnd',))

    def on_subject_notify__ownedEnd(self, subject, pspec):
        self.request_update()

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        cr.line_to(15, -10)
        cr.line_to(15, 10)
        cr.line_to(0, 0)
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.move_to(15, 0)

    def get_popup_menu(self):
        return self.popup_menu


# vim:sw=4:et:ai
