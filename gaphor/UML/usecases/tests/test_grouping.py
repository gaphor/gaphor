from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.classes import ComponentItem
from gaphor.UML.usecases import UseCaseItem


class TestSubsystemUseCaseGroup:
    def test_grouping(self, case):
        """Test adding an use case to a subsystem."""
        s = case.create(ComponentItem, UML.Component)
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)

        group(s.subject, uc1.subject)
        assert len(uc1.subject.subject) == 1
        group(s.subject, uc2.subject)
        assert len(uc2.subject.subject) == 1

        assert len(s.subject.useCase) == 2

    def test_grouping_with_namespace(self, case):
        """Test adding an use case to a subsystem (with namespace)"""
        s = case.create(ComponentItem, UML.Component)
        uc = case.create(UseCaseItem, UML.UseCase)

        group(s.subject, uc.subject)
        assert len(uc.subject.subject) == 1
        assert s.subject in uc.subject.subject

    def test_ungrouping(self, case):
        """Test removal of use case from subsystem."""
        s = case.create(ComponentItem, UML.Component)
        uc1 = case.create(UseCaseItem, UML.UseCase)
        uc2 = case.create(UseCaseItem, UML.UseCase)

        assert group(s.subject, uc1.subject)
        assert group(s.subject, uc2.subject)

        ungroup(s.subject, uc1.subject)
        assert len(uc1.subject.subject) == 0
        assert len(s.subject.useCase) == 1

        ungroup(s.subject, uc2.subject)
        assert len(uc2.subject.subject) == 0
        assert len(s.subject.useCase) == 0
