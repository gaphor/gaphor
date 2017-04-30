"""
Test transitions.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram.states.transition import TransitionItem
from gaphor.tests.testcase import TestCase


class TransitionTestCase(TestCase):
    """
    Test the working of transitions
    """

    def test_transition_guard(self):
        """Test events of transition.guard.
        """
        item = self.create(TransitionItem, uml2.Transition)
        assert item._guard.text == ''

        c = self.element_factory.create(uml2.Constraint)
        c.specification = 'blah'
        assert item._guard.text == ''

        item.subject.guard = c
        assert item.subject.guard is c
        assert item._guard.text == 'blah', item._guard.text

        del c.specification
        assert item._guard.text == '', item._guard.text

        c.specification = 'foo'
        assert item._guard.text == 'foo', item._guard.text

# vim:sw=4:et:ai
