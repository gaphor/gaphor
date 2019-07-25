"""
Test state items.
"""

from gaphor import UML
from gaphor.diagram.states.state import StateItem
from gaphor.tests.testcase import TestCase


class StateTestCase(TestCase):
    def test_state(self):
        """Test creation of states
        """
        self.create(StateItem, UML.State)

    def test_activities_persistence(self):
        """Test state activities saving/loading
        """
        # all activities
        s1 = self.create(StateItem, UML.State)
        s1.subject.name = "s1"
        s1.subject.entry = s1.model.create(UML.Activity)
        s1.subject.exit = s1.model.create(UML.Activity)
        s1.subject.doActivity = s1.model.create(UML.Activity)
        s1.subject.entry.name = "test 1 entry"
        s1.subject.exit.name = "test 1 exit"
        s1.subject.doActivity.name = "test 1 do"

        data = self.save()
        self.load(data)

        states = self.diagram.canvas.select(lambda e: isinstance(e, StateItem))
        assert 1 == len(states)
        s1 = states[0]

        assert "test 1 entry" == s1.subject.entry.name
        assert "test 1 exit" == s1.subject.exit.name
        assert "test 1 do" == s1.subject.doActivity.name
