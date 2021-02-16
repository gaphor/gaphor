"""Test include item connections."""

from gaphor import UML
from gaphor.UML.usecases.include import IncludeItem
from gaphor.UML.usecases.usecase import UseCaseItem


class TestIncludeItem:
    def test_use_case_glue(self, case):
        """Test "include" gluing to use cases."""

        uc1 = case.create(UseCaseItem, UML.UseCase)
        include = case.create(IncludeItem)

        glued = case.allow(include, include.head, uc1)
        assert glued

    def test_use_case_connect(self, case):
        """Test connecting "include" to use cases."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        include = case.create(IncludeItem)

        case.connect(include, include.head, uc1)
        assert case.get_connected(include.head), uc1

        case.connect(include, include.tail, uc2)
        assert case.get_connected(include.tail), uc2

    def test_use_case_reconnect(self, case):
        """Test reconnecting use cases with "include"."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        uc3 = case.create(UseCaseItem, UML.UseCase)
        include = case.create(IncludeItem)

        # connect: uc1 -> uc2
        case.connect(include, include.head, uc1)
        case.connect(include, include.tail, uc2)
        e = include.subject

        # reconnect: uc1 -> uc2
        case.connect(include, include.tail, uc3)

        assert e is include.subject
        assert include.subject.addition is uc1.subject
        assert include.subject.includingCase is uc3.subject

    def test_use_case_disconnect(self, case):
        """Test disconnecting "include" from use cases."""
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)
        include = case.create(IncludeItem)

        case.connect(include, include.head, uc1)
        case.connect(include, include.tail, uc2)

        case.disconnect(include, include.head)
        assert case.get_connected(include.head) is None
        assert include.subject is None

        case.disconnect(include, include.tail)
        assert case.get_connected(include.tail) is None
