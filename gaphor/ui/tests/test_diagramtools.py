import logging

from gi.repository import Gdk

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.classes import AssociationItem, ClassItem
from gaphor.tests import TestCase
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramShow

logging.basicConfig(level=logging.DEBUG)


class DiagramItemConnectorTestCase(TestCase):
    services = TestCase.services + ["main_window", "action_manager", "properties"]

    def setUp(self):
        super(DiagramItemConnectorTestCase, self).setUp()
        self.component_registry = self.get_service("component_registry")
        self.event_manager = self.get_service("event_manager")
        mw = self.get_service("main_window")
        mw.open()
        self.main_window = mw
        self.event_manager.handle(DiagramShow(self.diagram))

    def test_item_reconnect(self):
        # Setting the stage:
        ci1 = self.create(ClassItem, UML.Class)
        ci2 = self.create(ClassItem, UML.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        assert a.subject
        assert a.head_end.subject
        assert a.tail_end.subject

        the_association = a.subject

        # The act: perform button press event and button release
        view = self.component_registry.get(UIComponent, "diagrams").get_current_view()

        assert self.diagram.canvas is view.canvas

        p = view.get_matrix_i2v(a).transform_point(*a.head.pos)

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_PRESS,
            0,
        )

        view.do_event(event)

        assert the_association is a.subject

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_RELEASE,
            0,
        )

        view.do_event(event)

        assert the_association is a.subject
