from gaphor import UML
from gaphor.UML.states.transition import TransitionItem


def test_transition_guard(create, element_factory):
    """Test events of transition.guard."""
    item = create(TransitionItem, UML.Transition)
    guard = item.shape_middle
    assert guard.text() == ""

    c = element_factory.create(UML.Constraint)
    c.specification = "blah"
    assert guard.text() == ""

    item.subject.guard = c
    assert item.subject.guard is c
    assert guard.text() == "[blah]", guard.text()

    del c.specification
    assert guard.text() == "", guard.text()

    c.specification = "foo"
    assert guard.text() == "[foo]", guard.text()
