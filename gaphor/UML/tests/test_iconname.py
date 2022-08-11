from gaphor import UML
from gaphor.UML.iconname import get_name_for_pseudostate


def test_pseudostate_icon():
    element = UML.Pseudostate()
    element.kind = "initial"

    assert get_name_for_pseudostate(element) == "gaphor-initial-pseudostate-symbolic"
