"""Test extend item connections."""

from gaphor import UML
from gaphor.UML.usecases.extend import ExtendItem
from gaphor.UML.usecases.usecase import UseCaseItem


class TestExtendItem:
    def test_use_case_glue(self, case):
        """Test "extend" gluing to use cases."""

        uc1 = case.create(UseCaseItem, UML.UseCase)
        extend = case.create(ExtendItem)

        glued = case.allow(extend, extend.head, uc1)
        assert glued

    def test_use_case_connect(self, case):
        """Test connecting "extend" to use cases."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        extend = case.create(ExtendItem)

        case.connect(extend, extend.head, uc1)
        assert case.get_connected(extend.head), uc1

        case.connect(extend, extend.tail, uc2)
        assert case.get_connected(extend.tail), uc2

    def test_use_case_reconnect(self, case):
        """Test reconnecting use cases with "extend"."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        uc3 = case.create(UseCaseItem, UML.UseCase)
        extend = case.create(ExtendItem)

        # connect: uc1 -> uc2
        case.connect(extend, extend.head, uc1)
        case.connect(extend, extend.tail, uc2)
        e = extend.subject

        # reconnect: uc1 -> uc2
        case.connect(extend, extend.tail, uc3)

        assert e is not extend.subject
        assert extend.subject.extendedCase is uc1.subject
        assert extend.subject.extension is uc3.subject

    def test_use_case_disconnect(self, case):
        """Test disconnecting "extend" from use cases."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        extend = case.create(ExtendItem)

        case.connect(extend, extend.head, uc1)
        case.connect(extend, extend.tail, uc2)

        case.disconnect(extend, extend.head)
        assert case.get_connected(extend.head) is None
        assert extend.subject is None

        case.disconnect(extend, extend.tail)
        assert case.get_connected(extend.tail) is None
