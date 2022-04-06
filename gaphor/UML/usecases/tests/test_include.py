"""Test include item connections."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.usecases.include import IncludeItem
from gaphor.UML.usecases.usecase import UseCaseItem


def test_use_case_glue(create):
    """Test "include" gluing to use cases."""

    uc1 = create(UseCaseItem, UML.UseCase)
    include = create(IncludeItem)

    glued = allow(include, include.head, uc1)
    assert glued


def test_use_case_connect(create):
    """Test connecting "include" to use cases."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    include = create(IncludeItem)

    connect(include, include.head, uc1)
    assert get_connected(include, include.head), uc1

    connect(include, include.tail, uc2)
    assert get_connected(include, include.tail), uc2


def test_use_case_reconnect(create):
    """Test reconnecting use cases with "include"."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    uc3 = create(UseCaseItem, UML.UseCase)
    include = create(IncludeItem)

    # connect: uc1 -> uc2
    connect(include, include.head, uc1)
    connect(include, include.tail, uc2)
    e = include.subject

    # reconnect: uc1 -> uc2
    connect(include, include.tail, uc3)

    assert e is not include.subject
    assert include.subject.addition is uc1.subject
    assert include.subject.includingCase is uc3.subject


def test_use_case_disconnect(create):
    """Test disconnecting "include" from use cases."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    include = create(IncludeItem)

    connect(include, include.head, uc1)
    connect(include, include.tail, uc2)

    disconnect(include, include.head)
    assert get_connected(include, include.head) is None
    assert include.subject is None

    disconnect(include, include.tail)
    assert get_connected(include, include.tail) is None
