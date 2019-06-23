import pytest
from gaphor import UML
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.presentation import ElementPresentation
from gaphor.services.eventmanager import EventManager


class DummyVisualComponent:
    def size(self, cr):
        return 0, 0

    def draw(self, cr, bounding_box):
        pass


class TestElement(ElementPresentation):
    def __init__(self, id=None, model=None):
        super().__init__(id, model, layout=DummyVisualComponent())


@pytest.fixture
def element_factory():
    return ElementFactory(EventManager())


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(UML.Diagram)


def test_creation(element_factory):
    p = element_factory.create(UML.Presentation)

    assert p
    assert p.model
    assert p.subject is None


def test_element_saving(element_factory, diagram):
    subject = element_factory.create(UML.Class)
    p = diagram.create(TestElement, subject=subject)

    properties = {}
    referenced = set()

    def save_func(name, value, reference=False):
        properties[name] = value
        if reference:
            referenced.add(name)

    p.save(save_func)

    assert len(properties) == 4
    assert properties["matrix"] == (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    assert properties["width"] == 10.0
    assert properties["height"] == 10.0
    assert properties["subject"] is subject


def test_element_loading(element_factory, diagram):
    subject = element_factory.create(UML.Class)
    p = diagram.create(TestElement)

    p.load("matrix", "(2.0, 0.0, 0.0, 2.0, 0.0, 0.0)")
    p.load("width", "20")
    p.load("height", "25")
    p.load("subject", subject)

    assert tuple(p.matrix) == (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    assert p.width == 20
    assert p.height == 25
    assert p.subject is subject
