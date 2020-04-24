import pytest
from gaphas.canvas import Canvas, Context, instant_cairo_context

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.interactions.executionspecification import ExecutionSpecificationItem
from gaphor.UML.interactions.lifeline import LifelineItem


def test_draw_on_canvas():
    canvas = Canvas()
    exec_spec = ExecutionSpecificationItem()
    canvas.add(exec_spec)
    cr = instant_cairo_context()
    exec_spec.draw(Context(cairo=cr, dropzone=False))


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


def test_disconnect_execution_specification_from_lifeline(diagram, element_factory):
    def elements_of_kind(type):
        return element_factory.lselect(lambda e: e.isKindOf(type))

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
    assert elements_of_kind(UML.ExecutionSpecification) == []
    assert elements_of_kind(UML.ExecutionOccurrenceSpecification) == []


def test_allow_execution_specification_to_execution_specification(diagram):
    parent_exec_spec = diagram.create(ExecutionSpecificationItem)
    child_exec_spec = diagram.create(ExecutionSpecificationItem)

    glued = allow(
        parent_exec_spec,
        parent_exec_spec.handles()[0],
        child_exec_spec,
        child_exec_spec.ports()[0],
    )

    assert glued


def test_connect_execution_specification_to_execution_specification(
    diagram, element_factory
):
    parent_exec_spec = diagram.create(ExecutionSpecificationItem)
    child_exec_spec = diagram.create(ExecutionSpecificationItem)

    connect(
        child_exec_spec,
        child_exec_spec.handles()[0],
        parent_exec_spec,
        parent_exec_spec.ports()[0],
    )

    assert not parent_exec_spec.subject
    assert not child_exec_spec.subject


def test_connect_execution_specification_to_execution_specification_with_lifeline(
    diagram, element_factory
):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    parent_exec_spec = diagram.create(ExecutionSpecificationItem)
    child_exec_spec = diagram.create(ExecutionSpecificationItem)
    connect(
        parent_exec_spec,
        parent_exec_spec.handles()[0],
        lifeline,
        lifeline.lifetime.port,
    )

    connect(
        child_exec_spec,
        child_exec_spec.handles()[0],
        parent_exec_spec,
        parent_exec_spec.ports()[0],
    )

    assert child_exec_spec.subject
    assert lifeline.subject
    assert child_exec_spec.subject.start.covered is lifeline.subject
    assert (
        child_exec_spec.subject.executionOccurrenceSpecification[0].covered
        is lifeline.subject
    )


def test_connect_execution_specification_with_execution_specification_to_lifeline(
    diagram, element_factory
):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    parent_exec_spec = diagram.create(ExecutionSpecificationItem)
    child_exec_spec = diagram.create(ExecutionSpecificationItem)
    connect(
        child_exec_spec,
        child_exec_spec.handles()[0],
        parent_exec_spec,
        parent_exec_spec.ports()[0],
    )

    connect(
        parent_exec_spec,
        parent_exec_spec.handles()[0],
        lifeline,
        lifeline.lifetime.port,
    )

    assert parent_exec_spec.subject
    assert child_exec_spec.subject
    assert lifeline.subject
    assert parent_exec_spec.subject.start.covered is lifeline.subject
    assert child_exec_spec.subject.start.covered is lifeline.subject
    assert (
        child_exec_spec.subject.executionOccurrenceSpecification[0].covered
        is lifeline.subject
    )


def test_disconnect_execution_specification_with_execution_specification_from_lifeline(
    diagram, element_factory
):
    def elements_of_kind(type):
        return element_factory.lselect(lambda e: e.isKindOf(type))

    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    parent_exec_spec = diagram.create(ExecutionSpecificationItem)
    child_exec_spec = diagram.create(ExecutionSpecificationItem)
    grand_child_exec_spec = diagram.create(ExecutionSpecificationItem)
    connect(
        parent_exec_spec,
        parent_exec_spec.handles()[0],
        lifeline,
        lifeline.lifetime.port,
    )
    connect(
        child_exec_spec,
        child_exec_spec.handles()[0],
        parent_exec_spec,
        parent_exec_spec.ports()[0],
    )
    connect(
        grand_child_exec_spec,
        grand_child_exec_spec.handles()[0],
        child_exec_spec,
        child_exec_spec.ports()[0],
    )

    disconnect(parent_exec_spec, parent_exec_spec.handles()[0])

    assert lifeline.subject
    assert parent_exec_spec.subject is None
    assert child_exec_spec.subject is None
    assert grand_child_exec_spec.subject is None
    assert elements_of_kind(UML.ExecutionSpecification) == []
    assert elements_of_kind(UML.ExecutionOccurrenceSpecification) == []


def test_save_and_load(diagram, element_factory, saver, loader):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    exec_spec = diagram.create(ExecutionSpecificationItem)

    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)

    diagram.canvas.update_now()

    saved_data = saver()

    loader(saved_data)

    exec_specs = element_factory.lselect(
        lambda e: e.isKindOf(UML.ExecutionSpecification)
    )
    loaded_exec_spec = exec_specs[0].presentation[0]

    assert len(exec_specs) == 1
    assert (
        len(
            element_factory.lselect(
                lambda e: e.isKindOf(UML.ExecutionOccurrenceSpecification)
            )
        )
        == 2
    )
    assert loaded_exec_spec.canvas.get_connection(loaded_exec_spec.handles()[0])
