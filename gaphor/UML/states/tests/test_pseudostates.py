from gaphor import UML
from gaphor.UML.states.pseudostates import PseudostateItem


def test_initial_pseudostate(create):
    item = create(PseudostateItem, UML.Pseudostate)
    assert "initial" == item.subject.kind


def test_history_pseudostate(create):
    """Test creation of initial pseudostate."""
    item = create(PseudostateItem, UML.Pseudostate)
    # history setting is done in the DiagramToolbox factory:
    item.subject.kind = "shallowHistory"
    assert "shallowHistory" == item.subject.kind
