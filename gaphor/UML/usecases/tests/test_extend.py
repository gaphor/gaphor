"""Test extend item connections."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.usecases.extend import ExtendItem
from gaphor.UML.usecases.usecase import UseCaseItem


def test_use_case_glue(create):
    """Test "extend" gluing to use cases."""

    uc1 = create(UseCaseItem, UML.UseCase)
    extend = create(ExtendItem)

    glued = allow(extend, extend.head, uc1)
    assert glued


def test_use_case_connect(create):
    """Test connecting "extend" to use cases."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    extend = create(ExtendItem)

    connect(extend, extend.head, uc1)
    assert get_connected(extend, extend.head), uc1

    connect(extend, extend.tail, uc2)
    assert get_connected(extend, extend.tail), uc2


def test_use_case_reconnect(create):
    """Test reconnecting use cases with "extend"."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    uc3 = create(UseCaseItem, UML.UseCase)
    extend = create(ExtendItem)

    # connect: uc1 -> uc2
    connect(extend, extend.head, uc1)
    connect(extend, extend.tail, uc2)
    e = extend.subject

    # reconnect: uc1 -> uc2
    connect(extend, extend.tail, uc3)

    assert e is not extend.subject
    assert extend.subject.extendedCase is uc1.subject
    assert extend.subject.extension is uc3.subject


def test_use_case_disconnect(create):
    """Test disconnecting "extend" from use cases."""
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)
    extend = create(ExtendItem)

    connect(extend, extend.head, uc1)
    connect(extend, extend.tail, uc2)

    disconnect(extend, extend.head)
    assert get_connected(extend, extend.head) is None
    assert extend.subject is None

    disconnect(extend, extend.tail)
    assert get_connected(extend, extend.tail) is None
