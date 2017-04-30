from __future__ import absolute_import

import gtk
import logging

from gaphas.canvas import Context

from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase

Event = Context

logging.basicConfig(level=logging.DEBUG)


class DiagramItemConnectorTestCase(TestCase):
    services = TestCase.services + ['main_window', 'ui_manager', 'action_manager', 'properties']

    def setUp(self):
        super(DiagramItemConnectorTestCase, self).setUp()
        mw = self.get_service('main_window')
        mw.open()
        mw.show_diagram(self.diagram)
        self.main_window = mw

    def test_item_reconnect(self):
        # Setting the stage:
        ci1 = self.create(items.ClassItem, uml2.Class)
        ci2 = self.create(items.ClassItem, uml2.Class)
        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        self.assertTrue(a.subject)
        self.assertTrue(a.head_end.subject)
        self.assertTrue(a.tail_end.subject)

        the_association = a.subject

        # The act: perform button press event and button release
        view = self.main_window.get_current_diagram_view()

        self.assertSame(self.diagram.canvas, view.canvas)

        p = view.get_matrix_i2v(a).transform_point(*a.head.pos)

        event = Event(x=p[0], y=p[1], type=gtk.gdk.BUTTON_PRESS, state=0)

        view.do_event(event)

        self.assertSame(the_association, a.subject)

        event = Event(x=p[0], y=p[1], type=gtk.gdk.BUTTON_RELEASE, state=0)

        view.do_event(event)

        self.assertSame(the_association, a.subject)

# vim:sw=4:et:ai
