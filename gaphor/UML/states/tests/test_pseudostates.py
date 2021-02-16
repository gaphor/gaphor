"""Test pseudostates."""

from gaphor import UML
from gaphor.UML.states.pseudostates import PseudostateItem


class TestPseudostate:
    """Initial pseudostate item test cases."""

    def test_initial_pseudostate(self, case):
        """Test creation of initial pseudostate."""
        item = case.create(PseudostateItem, UML.Pseudostate)
        assert "initial" == item.subject.kind

    def test_history_pseudostate(self, case):
        """Test creation of initial pseudostate."""
        item = case.create(PseudostateItem, UML.Pseudostate)
        # history setting is done in the DiagramToolbox factory:
        item.subject.kind = "shallowHistory"
        assert "shallowHistory" == item.subject.kind
