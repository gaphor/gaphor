import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import connect
from gaphor.plugins.autolayout.pydot import AutoLayout, parse_edge_pos
from gaphor.UML.diagramitems import ClassItem, GeneralizationItem


def test_layout_diagram(diagram, create, event_manager):
    superclass = create(ClassItem, UML.Class)
    subclass = create(ClassItem, UML.Class)
    gen = create(GeneralizationItem, UML.Generalization)
    connect(gen, gen.tail, superclass)
    connect(gen, gen.head, subclass)

    auto_layout = AutoLayout(event_manager, None)
    auto_layout.layout(diagram)

    assert gen.head.pos != (0, 0)
    assert gen.tail.pos != (0, 0)


def test_parse_pos():
    points = parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0 7,8.0"')

    assert points == [(1.0, 2.0), (7.0, 8.0)]


def test_parse_pos_invalid_number_of_points():
    with pytest.raises(IndexError):
        parse_edge_pos('"1.0,2.0 3.0,4 5.0,6.0"')
