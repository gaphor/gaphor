"""
Test pseudostates.
"""

from gaphor import UML
from gaphor.diagram.states.pseudostates import InitialPseudostateItem
from gaphor.tests.testcase import TestCase

class InitialPseudostate(TestCase):
    """
    Initial pseudostate item test cases.
    """
    def test_initial_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(InitialPseudostateItem, UML.Pseudostate)
        assert item.subject.kind == 'initial'

