import pytest

from gaphor import UML
from gaphor.core.modeling import Dependency
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import diagramitems


class DummyVisualComponent:
    def size(self, ctx, bounding_box=None):
        return 0, 0

    def draw(self, ctx, bounding_box):
        pass


class StubElement(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, shape=DummyVisualComponent())


class StubLine(LinePresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, shape_middle=DummyVisualComponent())


def test_creation(diagram):
    p = diagram.create(StubElement)

    assert p
    assert p.model
    assert p.subject is None


def test_element_sides(diagram):
    p = diagram.create(StubElement)

    port_top, port_right, port_bottom, port_left = p.ports()

    assert p.port_side(port_top) == "top"
    assert p.port_side(port_right) == "right"
    assert p.port_side(port_bottom) == "bottom"
    assert p.port_side(port_left) == "left"


def test_element_saving(element_factory, diagram):
    subject = element_factory.create(UML.Class)
    p = diagram.create(StubElement, subject=subject)

    properties = {}
    referenced = set()

    def save_func(name, value, reference=False):
        properties[name] = value
        if reference:
            referenced.add(name)

    p.save(save_func)

    assert len(properties) == 6
    assert properties["matrix"] == (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    assert properties["width"] == pytest.approx(100.0)
    assert properties["height"] == pytest.approx(50.0)
    assert properties["top-left"] == (0, 0)
    assert properties["subject"] is subject
    assert properties["diagram"] is diagram


def test_element_loading(element_factory, diagram):
    subject = element_factory.create(UML.Class)
    p = diagram.create(StubElement)

    p.load("matrix", "(2.0, 0.0, 0.0, 2.0, 0.0, 0.0)")
    p.load("width", "200")
    p.load("height", "225")
    p.load("subject", subject)

    assert tuple(p.matrix) == (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    assert p.width == 200
    assert p.height == 225
    assert p.subject is subject


def test_line_saving(element_factory, diagram):
    subject = element_factory.create(Dependency)
    p = diagram.create(StubLine, subject=subject)

    properties = {}
    referenced = set()

    def save_func(name, value, reference=False):
        properties[name] = value
        if reference:
            referenced.add(name)

    p.save(save_func)

    assert properties["matrix"] == (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    assert properties["orthogonal"] is False
    assert properties["horizontal"] is False
    assert properties["points"] == [(0.0, 0.0), (10.0, 10.0)]
    assert properties["subject"] is subject
    assert "head-connection" not in properties
    assert "tail-connection" not in properties


def test_line_saving_without_subject(diagram):
    p = diagram.create(StubLine)

    properties = {}
    referenced = set()

    def save_func(name, value, reference=False):
        properties[name] = value
        if reference:
            referenced.add(name)

    p.save(save_func)

    assert "subject" not in properties


def test_line_loading(element_factory, diagram):
    with element_factory.block_events():
        subject = element_factory.create(Dependency)
        p = diagram.create(StubLine)

        p.load("matrix", "(2.0, 0.0, 0.0, 2.0, 0.0, 0.0)")
        p.load("orthogonal", "0")
        p.load("horizontal", "1")
        p.load("points", "[(1.0, 2.0), (3.0, 4.0)]")
        p.load("subject", subject)

    assert tuple(p.matrix) == (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)
    assert not p.orthogonal
    assert p.horizontal
    assert tuple(p.handles()[0].pos) == (1.0, 2.0)
    assert tuple(p.handles()[1].pos) == (3.0, 4.0)
    assert p.subject is subject


def test_remove_connected_items_on_unlink(create, diagram):
    class_a_item = create(diagramitems.ClassItem, UML.Class)
    class_b_item = create(diagramitems.ClassItem, UML.Class)
    association_item = create(diagramitems.AssociationItem)

    connect(association_item, association_item.head, class_a_item)
    connect(association_item, association_item.tail, class_b_item)

    class_a_item.subject.unlink()

    assert class_a_item not in diagram.ownedPresentation
    assert association_item in diagram.ownedPresentation
    assert class_b_item in diagram.ownedPresentation
