"""Test transitions."""

from gaphor import UML
from gaphor.UML.states.transition import TransitionItem


class TestTransition:
    """Test the working of transitions."""

    def test_transition_guard(self, case):
        """Test events of transition.guard."""
        item = case.create(TransitionItem, UML.Transition)
        guard = item.shape_middle
        assert guard.text() == ""

        c = case.element_factory.create(UML.Constraint)
        c.specification = "blah"
        assert guard.text() == ""

        item.subject.guard = c
        assert item.subject.guard is c
        assert guard.text() == "[blah]", guard.text()

        del c.specification
        assert guard.text() == "", guard.text()

        c.specification = "foo"
        assert guard.text() == "[foo]", guard.text()
