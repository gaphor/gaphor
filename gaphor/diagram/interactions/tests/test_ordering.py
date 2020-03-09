from gaphor import UML
from gaphor.diagram.interactions.executionspecification import (
    ExecutionSpecificationItem,
)
from gaphor.diagram.interactions.interactionsconnect import order_lifeline_covered_by
from gaphor.diagram.interactions.lifeline import LifelineItem
from gaphor.diagram.interactions.message import MessageItem
from gaphor.diagram.tests.fixtures import connect


def test_ordering(diagram, element_factory):
    lifeline = diagram.create(
        LifelineItem, subject=element_factory.create(UML.Lifeline)
    )
    lifeline.lifetime.visible = True
    lifeline.lifetime.bottom.pos.y = 1000
    lifetime_top = lifeline.lifetime.top.pos

    exec_spec = diagram.create(ExecutionSpecificationItem)
    message1 = diagram.create(MessageItem)
    message2 = diagram.create(MessageItem)
    message3 = diagram.create(MessageItem)

    message1.head.pos.y = lifetime_top.y + 300
    exec_spec.top.pos.y = lifetime_top.y + 400
    message2.head.pos.y = lifetime_top.y + 500
    exec_spec.bottom.pos.y = lifetime_top.y + 600
    message3.tail.pos.y = lifetime_top.y + 700

    # Add in "random" order
    connect(exec_spec, exec_spec.handles()[0], lifeline, lifeline.lifetime.port)
    connect(message3, message3.tail, lifeline, lifeline.lifetime.port)
    connect(message1, message1.head, lifeline, lifeline.lifetime.port)
    connect(message2, message2.head, exec_spec, exec_spec.ports()[1])

    occurrences = [
        message1.subject.sendEvent,
        exec_spec.subject.start,
        message2.subject.sendEvent,
        exec_spec.subject.finish,
        message3.subject.receiveEvent,
    ]

    order_lifeline_covered_by(lifeline)

    assert list(lifeline.subject.coveredBy) == occurrences
