"""Test state items."""

from gaphor import UML
from gaphor.UML.states.state import StateItem


class TestState:
    def test_state(self, case):
        """Test creation of states."""
        case.create(StateItem, UML.State)

    def test_activities_persistence(self, case):
        """Test state activities saving/loading."""
        # all activities
        s1 = case.create(StateItem, UML.State)
        s1.subject.name = "s1"
        s1.subject.entry = s1.model.create(UML.Activity)
        s1.subject.exit = s1.model.create(UML.Activity)
        s1.subject.doActivity = s1.model.create(UML.Activity)
        s1.subject.entry.name = "test 1 entry"
        s1.subject.exit.name = "test 1 exit"
        s1.subject.doActivity.name = "test 1 do"

        data = case.save()
        case.load(data)

        s1 = next(case.diagram.select(StateItem))
        assert "test 1 entry" == s1.subject.entry.name
        assert "test 1 exit" == s1.subject.exit.name
        assert "test 1 do" == s1.subject.doActivity.name
