"""
Test pseudostates.
"""

from gaphor import UML
from gaphor.tests.testcase import TestCase
from gaphor.UML.states.pseudostates import PseudostateItem


class Pseudostate(TestCase):
    """
    Initial pseudostate item test cases.
    """

    def test_initial_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(PseudostateItem, UML.Pseudostate)
        assert "initial" == item.subject.kind

    def test_history_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(PseudostateItem, UML.Pseudostate)
        # history setting is done in the DiagramToolbox factory:
        item.subject.kind = "shallowHistory"
        assert "shallowHistory" == item.subject.kind
