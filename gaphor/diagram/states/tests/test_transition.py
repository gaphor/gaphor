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
        assert item._guard.text == ""

        c = self.element_factory.create(UML.Constraint)
        c.specification = "blah"
        assert item._guard.text == ""

        item.subject.guard = c
        assert item.subject.guard is c
        assert item._guard.text == "blah", item._guard.text

        del c.specification
        assert item._guard.text == "", item._guard.text

        c.specification = "foo"
        assert item._guard.text == "foo", item._guard.text


# vim:sw=4:et:ai
