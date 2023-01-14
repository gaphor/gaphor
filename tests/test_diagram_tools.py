import pytest
from gi.repository import Gdk, Gtk

from gaphor import UML
from gaphor.application import Session
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramOpened
from gaphor.UML.classes import AssociationItem, ClassItem


@pytest.fixture
def session():
    session = Session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "element_dispatcher",
            "modeling_language",
            "sanitizer",
            "main_window",
            "properties",
            "model_browser",
            "diagrams",
            "toolbox",
            "export_menu",
            "tools_menu",
            "elementeditor",
        ]
    )
    session.get_service("main_window").open()
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def component_registry(session):
    return session.get_service("component_registry")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(event_manager, element_factory):
    diagram = element_factory.create(Diagram)
    event_manager.handle(DiagramOpened(diagram))
    return diagram


@pytest.mark.skipif(Gtk.get_major_version() != 3, reason="Works only for GTK+ 3")
def test_item_reconnect(diagram, component_registry, element_factory):
    # Setting the stage:
    ci1 = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    ci2 = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    a = diagram.create(AssociationItem)

    connect(a, a.head, ci1)
    connect(a, a.tail, ci2)

    assert a.subject
    assert a.head_subject
    assert a.tail_subject

    the_association = a.subject

    # The act: perform button press event and button release
    view = component_registry.get(UIComponent, "diagrams").get_current_view()

    assert diagram is view.model

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
