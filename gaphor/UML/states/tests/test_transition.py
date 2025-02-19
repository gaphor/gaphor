from gaphor import UML
from gaphor.UML.states.transition import TransitionItem


def test_transition_guard(create, element_factory):
    """Test events of transition.guard."""
    item = create(TransitionItem, UML.Transition)
    guard = item.shape_middle
    assert guard.child.text() == ""

    c = element_factory.create(UML.Constraint)
    specification = element_factory.create(UML.LiteralString)
    specification.owningConstraint = c
    specification.value = "blah"
    c.specification = specification
    assert guard.child.text() == ""

    item.subject.guard = c
    assert item.subject.guard is c
    assert guard.child.text() == "[blah]", guard.text()

    del c.specification
    assert guard.child.text() == "", guard.text()

    specification.value = "foo"
    c.specification = specification
    assert guard.child.text() == "[foo]", guard.text()
