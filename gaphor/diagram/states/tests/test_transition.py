"""
Test transitions.
"""

from gaphor import UML
from gaphor.diagram.states.transition import TransitionItem
from gaphor.tests.testcase import TestCase


class TransitionTestCase(TestCase):
    """
    Test the working of transitions
    """

    def test_transition_guard(self):
        """Test events of transition.guard.
        """
        item = self.create(TransitionItem, UML.Transition)
        guard = item.shape_middle
        assert guard.text() == ""

        c = self.element_factory.create(UML.Constraint)
        c.specification = "blah"
        assert guard.text() == ""

        item.subject.guard = c
        assert item.subject.guard is c
        assert guard.text() == "blah", guard.text()

        del c.specification
        assert guard.text() == "", guard.text()

        c.specification = "foo"
        assert guard.text() == "foo", item._guard.text()
