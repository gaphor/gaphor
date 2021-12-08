"""Every now and then I run into an issue where a derived union returns a
unioncache.

It looks like there is a unioncache packed in a unioncache.

What makes the issue even more weird is that the derived field is not even assigned on this type.
"""

import pytest

from gaphor import UML
from gaphor.application import Session
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import diagramitems


@pytest.fixture
def session():
    session = Session()
    yield session
    session.shutdown()


@pytest.fixture
def event_manager(session):
    return session.get_service("event_manager")


@pytest.fixture
def element_factory(session):
    return session.get_service("element_factory")


@pytest.fixture
def diagram(element_factory, event_manager):
    with Transaction(event_manager):
        return element_factory.create(Diagram)


def test_unioncache_in_derived_union(diagram, event_manager, element_factory):
    with Transaction(event_manager):
        uc1 = diagram.create(
            diagramitems.UseCaseItem, subject=element_factory.create(UML.UseCase)
        )
        uc2 = diagram.create(
            diagramitems.UseCaseItem, subject=element_factory.create(UML.UseCase)
        )
        include = diagram.create(diagramitems.IncludeItem)

        connect(include, include.handles()[0], uc1)
        connect(include, include.handles()[1], uc2)

    assert uc1.subject in include.subject.target
    assert include.subject.ownedElement == []
