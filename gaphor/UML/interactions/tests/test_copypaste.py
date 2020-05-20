from gaphor import UML
from gaphor.diagram.tests.fixtures import connect, copy_clear_and_paste
from gaphor.UML.interactions import LifelineItem, MessageItem
from gaphor.UML.interactions.tests.test_executionspecification import (
    create_lifeline_with_execution_specification,
)


def test_message(diagram, element_factory):
    lifeline1 = element_factory.create(UML.Lifeline)
    lifeline2 = element_factory.create(UML.Lifeline)

    lifeline1_item = diagram.create(LifelineItem, subject=lifeline1)
    lifeline2_item = diagram.create(LifelineItem, subject=lifeline2)
    message_item = diagram.create(MessageItem)

    connect(message_item, message_item.handles()[0], lifeline1_item)
    connect(message_item, message_item.handles()[1], lifeline2_item)

    copy_clear_and_paste(
        {lifeline1_item, lifeline2_item, message_item}, diagram, element_factory
    )

    new_message: UML.Message = element_factory.lselect(
        lambda e: isinstance(e, UML.Message)
    )[0]
    new_lifelines = element_factory.lselect(lambda e: isinstance(e, UML.Lifeline))

    assert new_message.sendEvent.covered in new_lifelines
    assert new_message.receiveEvent.covered in new_lifelines
    assert new_message.sendEvent.covered is not new_message.receiveEvent.covered


def test_execution_specification(diagram, element_factory):
    lifeline_item, exec_spec_item = create_lifeline_with_execution_specification(
        diagram, element_factory
    )

    copy_clear_and_paste({lifeline_item, exec_spec_item}, diagram, element_factory)

    new_exec_spec: UML.ExecutionSpecification = element_factory.lselect(
        lambda e: isinstance(e, UML.ExecutionSpecification)
    )[0]
    new_lifeline: UML.Lifeline = element_factory.lselect(
        lambda e: isinstance(e, UML.Lifeline)
    )[0]

    assert (
        new_lifeline.coveredBy[0] is new_exec_spec.executionOccurrenceSpecification[0]
    )
    assert (
        new_lifeline.coveredBy[1] is new_exec_spec.executionOccurrenceSpecification[1]
    )
