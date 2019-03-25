import logging

from gi.repository import Gdk

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram import items
from gaphor.tests import TestCase
from gaphor.ui.event import Diagram
from gaphor.ui.interfaces import IUIComponent

logging.basicConfig(level=logging.DEBUG)


class DiagramItemConnectorTestCase(TestCase):
    services = TestCase.services + [
        "main_window",
        "ui_manager",
        "action_manager",
        "properties",
    ]
    component_registry = inject("component_registry")

    def setUp(self):
        super(DiagramItemConnectorTestCase, self).setUp()
        mw = self.get_service("main_window")
        mw.open()
        self.main_window = mw
        self.component_registry.handle(Diagram(self.diagram))

    def test_item_reconnect(self):
        # Setting the stage:
        ci1 = self.create(items.ClassItem, UML.Class)
        ci2 = self.create(items.ClassItem, UML.Class)
        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        self.assertTrue(a.subject)
        self.assertTrue(a.head_end.subject)
        self.assertTrue(a.tail_end.subject)

        the_association = a.subject

        # The act: perform button press event and button release
        view = self.component_registry.get_utility(
            IUIComponent, "diagrams"
        ).get_current_view()

        self.assertSame(self.diagram.canvas, view.canvas)

        p = view.get_matrix_i2v(a).transform_point(*a.head.pos)

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_PRESS,
            0,
        )

        view.do_event(event)

        self.assertSame(the_association, a.subject)

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_RELEASE,
            0,
        )

        view.do_event(event)

        self.assertSame(the_association, a.subject)
