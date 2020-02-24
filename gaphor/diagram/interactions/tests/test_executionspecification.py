import pytest
from gaphas.canvas import Canvas, Context, instant_cairo_context
from gaphas.view import Context

from gaphor import UML
from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.diagram.interactions.lifeline import LifelineItem
from gaphor.diagram.tests.fixtures import allow, connect, disconnect


def test_draw_on_canvas():
    canvas = Canvas()
    exec_spec = ExecutionSpecificationItem()
    canvas.add(exec_spec)
    cr = instant_cairo_context()
    exec_spec.draw(Context(cairo=cr))


def test_allow_execution_specification_to_lifeline(diagram):
    lifeline = diagram.create(LifelineItem)
    lifeline.lifetime.visible = True
    exec_spec = diagram.create(ExecutionSpecificationItem)

    glued = allow(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    assert glued


def test_connect_execution_specification_to_lifeline(diagram, element_factory):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    exec_spec = diagram.create(ExecutionSpecificationItem)

    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    assert exec_spec.subject
    assert lifeline.subject
    assert exec_spec.subject.start.covered is lifeline.subject
    assert (
        exec_spec.subject.executionOccurrenceSpecification[0].covered
        is lifeline.subject
    )


def test_connect_execution_specification_to_lifeline(diagram, element_factory):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    exec_spec = diagram.create(ExecutionSpecificationItem)
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    disconnect(exec_spec, exec_spec.handles()[0])

    assert lifeline.subject
    assert exec_spec.subject is None
    assert exec_spec.canvas
    assert (
        element_factory.lselect(lambda e: e.isKindOf(UML.ExecutionSpecification)) == []
    )
    assert (
        element_factory.lselect(
            lambda e: e.isKindOf(UML.ExecutionOccurrenceSpecification)
        )
        == []
    )
