from gaphas.constraint import BaseConstraint
from gaphas.item import Item
from gaphas.solver import Variable

from gaphor.core.eventmanager import event_handler
from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.event import DiagramItemDeleted
from gaphor.core.modeling.presentation import Presentation


class Example(Presentation, Item):
    pass


def test_presentation_implements_item_protocol(diagram):
    presentation = diagram.create(Example)

    assert isinstance(presentation, Item)


def test_presentation_should_have_a_diagram(diagram):
    presentation = diagram.create(Example)

    assert presentation.diagram is diagram


def test_should_emit_event_when_unlinked(diagram, event_manager):
    presentation = diagram.create(Example)
    events = []

    @event_handler(DiagramItemDeleted)
    def handler(event):
        events.append(event)

    event_manager.subscribe(handler)

    presentation.unlink()

    assert events
    assert events[0].diagram is diagram
    assert events[0].element is presentation


def test_presentation_should_unlink_when_diagram_changes(diagram):
    presentation = diagram.create(Example)
    diagram.connections.add_constraint(presentation, BaseConstraint(Variable()))
    assert len(list(diagram.connections.get_connections(item=presentation))) == 1

    presentation.diagram = None

    assert not list(diagram.connections.get_connections(item=presentation))


def test_presentation_can_not_set_new_diagram(diagram, element_factory):
    presentation = diagram.create(Example)
    new_diagram = element_factory.create(Diagram)

    presentation.diagram = new_diagram

    assert presentation.diagram is None


def test_should_emit_event_when_diagram_changes(diagram, event_manager):
    presentation = diagram.create(Example)
    events = []

    @event_handler(DiagramItemDeleted)
    def handler(event):
        events.append(event)

    event_manager.subscribe(handler)

    del presentation.diagram

    assert events
    assert events[0].diagram is diagram
    assert events[0].element is presentation
