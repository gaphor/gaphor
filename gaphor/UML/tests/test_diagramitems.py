import pytest

from gaphor.core.modeling import NamedElement, Presentation
from gaphor.diagram.general import CommentLineItem
from gaphor.diagram.presentation import Named
from gaphor.diagram.support import get_model_element
from gaphor.UML import diagramitems


def _issubclass(child, parent):
    try:
        return issubclass(child, parent)
    except TypeError:
        return False


def all_items_and_elements():
    return [
        [cls, get_model_element(cls)]
        for cls in diagramitems.__dict__.values()
        if _issubclass(cls, Presentation) and get_model_element(cls)
    ]


@pytest.mark.parametrize(
    "item_class",
    [cls for cls in diagramitems.__dict__.values() if _issubclass(cls, Presentation)],
)
def test_all_diagram_items_have_a_model_element_mapping(item_class):
    if item_class is CommentLineItem:
        assert not get_model_element(item_class)
    else:
        assert get_model_element(item_class)


NAMED_EXCLUSIONS = [
    diagramitems.DependencyItem,
    diagramitems.ImplementationItem,
    diagramitems.ExecutionSpecificationItem,
]


@pytest.mark.parametrize(
    "item_class,element_class", all_items_and_elements(),
)
def test_all_named_elements_have_named_items(item_class, element_class):
    if item_class in NAMED_EXCLUSIONS:
        return

    if issubclass(element_class, NamedElement):
        assert issubclass(item_class, Named)

    if issubclass(item_class, Named):
        assert issubclass(element_class, NamedElement)
