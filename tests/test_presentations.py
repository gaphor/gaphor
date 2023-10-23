import itertools

import pytest

from gaphor.C4Model import diagramitems as c4_diagramitems
from gaphor.core.modeling.element import Element
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.support import get_diagram_item_metadata, get_model_element
from gaphor.RAAML import diagramitems as raaml_diagramitems
from gaphor.SysML import diagramitems as sysml_diagramitems
from gaphor.UML import diagramitems as uml_diagramitems

diagramitems = [
    c
    for c in itertools.chain.from_iterable(
        diagramitems.__dict__.values()
        for diagramitems in (
            uml_diagramitems,
            sysml_diagramitems,
            raaml_diagramitems,
            c4_diagramitems,
        )
    )
    if isinstance(c, type)
]

blacklist = [
    # These lines have no subject of their own
    uml_diagramitems.Line,
    uml_diagramitems.CommentLineItem,
    uml_diagramitems.ContainmentItem,
    # These lines have extra objects at the line ends
    uml_diagramitems.AssociationItem,
    uml_diagramitems.ConnectorItem,
    uml_diagramitems.ExtensionItem,
    uml_diagramitems.MessageItem,
]


@pytest.mark.parametrize(
    "diagram_item",
    [p for p in diagramitems if issubclass(p, LinePresentation) and p not in blacklist],
)
def test_line_presentations_have_metadata(diagram_item):
    metadata = get_diagram_item_metadata(diagram_item)
    element_class = get_model_element(diagram_item)

    assert metadata
    assert "head" in metadata
    assert "tail" in metadata
    assert issubclass(element_class, Element)
    assert metadata["head"] in element_class.umlproperties()
    assert metadata["tail"] in element_class.umlproperties()
