import logging

import pytest
from gi.repository import Gdk

from gaphor import UML
from gaphor.conftest import Case
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramOpened
from gaphor.UML.classes import AssociationItem, ClassItem

logging.basicConfig(level=logging.DEBUG)


class DiagramItemConnectorCase(Case):
    services = Case.services + [
        "main_window",
        "properties",
        "namespace",
        "diagrams",
        "toolbox",
        "export_menu",
        "tools_menu",
        "elementeditor",
    ]

    def __init__(self):
        super().__init__()
        self.component_registry = self.get_service("component_registry")
        self.event_manager = self.get_service("event_manager")
        mw = self.get_service("main_window")
        mw.open()
        self.main_window = mw
        self.event_manager.handle(DiagramOpened(self.diagram))


class TestDiagramConnector:
    @pytest.fixture(scope="module")
    def case(self):
        case = DiagramItemConnectorCase()
        yield case
        case.shutdown()

    def test_item_reconnect(self, case):
        # Setting the stage:
        ci1 = case.create(ClassItem, UML.Class)
        ci2 = case.create(ClassItem, UML.Class)
        a = case.create(AssociationItem)

        case.connect(a, a.head, ci1)
        case.connect(a, a.tail, ci2)

        assert a.subject
        assert a.head_subject
        assert a.tail_subject

        the_association = a.subject

        # The act: perform button press event and button release
        view = case.component_registry.get(UIComponent, "diagrams").get_current_view()

        assert case.diagram is view.model

        p = view.get_matrix_i2v(a).transform_point(*a.head.pos)

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_PRESS,
            0,
        )

        view.event(event)

        assert the_association is a.subject

        event = Gdk.Event()
        event.x, event.y, event.type, event.state = (
            p[0],
            p[1],
            Gdk.EventType.BUTTON_RELEASE,
            0,
        )

        view.event(event)

        assert the_association is a.subject
