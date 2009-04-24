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
        self.assertFalse(item._connected) # not connected by default


    def test_history_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(HistoryPseudostateItem, UML.Pseudostate)
        self.assertEquals('shallowHistory', item.subject.kind)
        self.assertFalse(item._connected) # not connected by default


# vim:sw=4:et:ai
