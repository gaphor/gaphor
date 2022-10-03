from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.classes import ComponentItem
from gaphor.UML.usecases import UseCaseItem


def test_grouping(create):
    """Test adding a use case to a subsystem."""
    s = create(ComponentItem, UML.Component)
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)

    group(s.subject, uc1.subject)
    assert len(uc1.subject.subject) == 1
    group(s.subject, uc2.subject)
    assert len(uc2.subject.subject) == 1

    assert len(s.subject.useCase) == 2


def test_grouping_with_namespace(create):
    """Test adding a use case to a subsystem (with namespace)"""
    s = create(ComponentItem, UML.Component)
    uc = create(UseCaseItem, UML.UseCase)

    group(s.subject, uc.subject)
    assert len(uc.subject.subject) == 1
    assert s.subject in uc.subject.subject


def test_ungrouping(create):
    """Test removal of use case from subsystem."""
    s = create(ComponentItem, UML.Component)
    uc1 = create(UseCaseItem, UML.UseCase)
    uc2 = create(UseCaseItem, UML.UseCase)

    assert group(s.subject, uc1.subject)
    assert group(s.subject, uc2.subject)

    ungroup(s.subject, uc1.subject)
    assert len(uc1.subject.subject) == 0
    assert len(s.subject.useCase) == 1

    ungroup(s.subject, uc2.subject)
    assert len(uc2.subject.subject) == 0
    assert len(s.subject.useCase) == 0
