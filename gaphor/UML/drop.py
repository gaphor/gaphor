from __future__ import annotations

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import drop, drop_relationship


@drop.register(UML.Association, Diagram)
def drop_association(element: UML.Association, diagram: Diagram, x, y):
    return drop_relationship(
        element, element.memberEnd[0].type, element.memberEnd[1].type, diagram, x, y
    )


@drop.register(UML.Connector, Diagram)
def drop_connector(element: UML.Connector, diagram: Diagram, x, y):
    return drop_relationship(
        element, element.end[0].role, element.end[1].role, diagram, x, y
    )


@drop.register(UML.Message, Diagram)
def drop_message(element: UML.Message, diagram: Diagram, x, y):
    return drop_relationship(
        element,
        element.sendEvent.covered
        if isinstance(element.sendEvent, UML.MessageOccurrenceSpecification)
        else None,
        element.receiveEvent.covered
        if isinstance(element.receiveEvent, UML.MessageOccurrenceSpecification)
        else None,
        diagram,
        x,
        y,
    )
