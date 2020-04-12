"""
Test pseudostates.
"""

from gaphor import UML
from gaphor.tests.testcase import TestCase
from gaphor.UML.states.pseudostates import (
    HistoryPseudostateItem,
    InitialPseudostateItem,
)


class InitialPseudostate(TestCase):
    """
    Initial pseudostate item test cases.
    """

    def test_initial_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(InitialPseudostateItem, UML.Pseudostate)
        assert "initial" == item.subject.kind

    def test_history_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(HistoryPseudostateItem, UML.Pseudostate)
        # history setting is done in the DiagramToolbox factory:
        item.subject.kind = "shallowHistory"
        assert "shallowHistory" == item.subject.kind
