"""
Test pseudostates.
"""

from gaphor import UML
from gaphor.diagram.states.pseudostates import InitialPseudostateItem, HistoryPseudostateItem
from gaphor.tests.testcase import TestCase


class InitialPseudostate(TestCase):
    """
    Initial pseudostate item test cases.
    """

    def test_initial_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(InitialPseudostateItem, UML.Pseudostate)
        self.assertEquals('initial', item.subject.kind)


    def test_history_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(HistoryPseudostateItem, UML.Pseudostate)
        # history setting is done in the DiagramToolbox factory:
        item.subject.kind = 'shallowHistory'
        self.assertEquals('shallowHistory', item.subject.kind)


# vim:sw=4:et:ai
