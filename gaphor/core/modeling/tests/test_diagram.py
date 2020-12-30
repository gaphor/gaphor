import gaphas
import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory, Presentation, StyleSheet
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.UML.modelinglanguage import UMLModelingLanguage


class Example(gaphas.Element, Presentation):
    def __init__(self, diagram, id):
        super().__init__(connections=diagram.connections, diagram=diagram, id=id)

    def unlink(self):
        self.test_unlinked = True
        super().unlink()


@pytest.fixture
def element_factory():
    event_manager = EventManager()
    element_dispatcher = ElementDispatcher(event_manager, UMLModelingLanguage())
    element_factory = ElementFactory(event_manager, element_dispatcher)
    yield element_factory
    element_factory.shutdown()
    element_dispatcher.shutdown()
    event_manager.shutdown()


def test_diagram_can_be_used_as_gtkview_model():
    diagram = Diagram("id", None)

    assert isinstance(diagram, gaphas.view.model.Model)


def test_canvas_is_saved():
    diagram = Diagram("id", None)
    saved_keys = []
    diagram.save(lambda name, val: saved_keys.append(name))

    assert "canvas" in saved_keys


def test_canvas_item_is_created(element_factory):
    diagram = element_factory.create(Diagram)
    example = diagram.create(Example)

    assert example in diagram.get_all_items()
    assert example.diagram is diagram


def test_canvas_is_unlinked(element_factory):
    diagram = element_factory.create(Diagram)
    example = diagram.create(Example)

    diagram.unlink()

    assert example.test_unlinked


def test_can_only_add_diagram_items(element_factory):
    diagram = element_factory.create(Diagram)

    with pytest.raises(TypeError):
        diagram.create(Diagram)


def test_diagram_stylesheet(element_factory):
    diagram = element_factory.create(Diagram)
    styleSheet = element_factory.create(StyleSheet)

    assert diagram.styleSheet is styleSheet


class ViewMock:
    def __init__(self):
        self.removed_items = set()

    def request_update(self, items, matrix_only_items, removed_items) -> None:
        self.removed_items.update(removed_items)


def test_remove_presentation_triggers_view(element_factory):
    diagram = element_factory.create(Diagram)
    print(diagram.watcher())
    view = ViewMock()
    diagram.register_view(view)

    example = diagram.create(Example)

    example.unlink()

    assert example.diagram is None
    assert example not in diagram.ownedPresentation
    assert example in view.removed_items
