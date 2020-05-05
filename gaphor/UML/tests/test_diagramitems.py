import pytest

from gaphor.core.modeling import Presentation
from gaphor.diagram.general import CommentLineItem
from gaphor.diagram.support import get_model_element
from gaphor.UML import diagramitems


def _issubclass(child, parent):
    try:
        return issubclass(child, parent)
    except TypeError:
        return False


@pytest.mark.parametrize(
    "item_class",
    [cls for cls in diagramitems.__dict__.values() if _issubclass(cls, Presentation)],
)
def test_all_diagram_items_have_a_model_element_mapping(item_class):
    if item_class is CommentLineItem:
        assert not get_model_element(item_class)
    else:
        assert get_model_element(item_class)
