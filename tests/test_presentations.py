import itertools

import pytest

from gaphor.C4Model import diagramitems as c4_diagramitems
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.support import get_diagram_item_metadata
from gaphor.RAAML import diagramitems as raaml_diagramitems
from gaphor.SysML import diagramitems as sysml_diagramitems
from gaphor.UML import diagramitems as uml_diagramitems

diagramitems = [
    c
    for c in itertools.chain(
        *(
            diagramitems.__dict__.values()
            for diagramitems in (
                uml_diagramitems,
                sysml_diagramitems,
                raaml_diagramitems,
                c4_diagramitems,
            )
        )
    )
    if isinstance(c, type)
]

blacklist = [
    uml_diagramitems.Line,
    uml_diagramitems.CommentLineItem,
    uml_diagramitems.ContainmentItem,
    uml_diagramitems.AssociationItem,
]


@pytest.mark.xfail
@pytest.mark.parametrize(
    "diagram_item",
    [p for p in diagramitems if issubclass(p, LinePresentation) and p not in blacklist],
)
def test_line_presentations_have_metadata(diagram_item):
    metadata = get_diagram_item_metadata(diagram_item)

    assert metadata
    assert "head" in metadata
    assert "tail" in metadata
