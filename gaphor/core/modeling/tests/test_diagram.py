import gaphas
import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory, Presentation
from gaphor.UML import Diagram


class Example(Presentation, gaphas.Element):
    def unlink(self):
        self.test_unlinked = True
        super().unlink()


@pytest.fixture
def element_factory():
    event_manager = EventManager()
    element_factory = ElementFactory()
    yield element_factory
    element_factory.shutdown()
    event_manager.shutdown()


def test_canvas_is_set_up():
    diagram = Diagram("id", None)

    assert diagram.canvas


def test_canvas_is_saved():
    diagram = Diagram("id", None)
    saved_keys = []
    diagram.save(lambda name, val: saved_keys.append(name))

    assert "canvas" in saved_keys


def test_canvas_item_is_created(element_factory):
    diagram = element_factory.create(Diagram)
    example = diagram.create(Example)

    assert example in diagram.canvas.get_all_items()


def test_canvas_is_unlinked(element_factory):
    diagram = element_factory.create(Diagram)
    example = diagram.create(Example)

    diagram.unlink()

    assert example.test_unlinked


def test_can_only_add_diagram_items(element_factory):
    diagram = element_factory.create(Diagram)

    with pytest.raises(TypeError):
        diagram.create(Diagram)
