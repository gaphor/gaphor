"""For all relevant model elements, check if there is at least one "owner"
("owner" is a derived union).

This is needed to display all elements in the tree view.

NOTE: Comment does not have an owner. In the model it does, though.
"""

import itertools

import pytest

import gaphor.SysML.diagramitems
import gaphor.UML.diagramitems
from gaphor import UML
from gaphor.core.modeling import Comment, Element
from gaphor.core.modeling.properties import derived
from gaphor.diagram.support import get_model_element


def all_subset_properties(prop):
    for sub in prop.subsets:
        if isinstance(sub, derived):
            yield from all_subset_properties(sub)
        else:
            yield sub


def all_presented_elements(module):
    return (
        get_model_element(getattr(module, name))
        for name in dir(module)
        if not name.startswith("_")
        and get_model_element(getattr(module, name) not in (None, Comment))
    )


def all_presented_uml_and_sysml_elements():
    return itertools.chain(
        all_presented_elements(gaphor.UML.diagramitems),
        all_presented_elements(gaphor.SysML.diagramitems),
        [
            UML.ExecutionOccurrenceSpecification,
            UML.ExtensionEnd,
            UML.MessageOccurrenceSpecification,
        ],
    )


def concrete_owner_property(class_):
    return (
        p for p in class_.umlproperties() if p in all_subset_properties(Element.owner)
    )


def test_all_presented_uml_and_sysml_elements():
    elements = all_presented_uml_and_sysml_elements()
    assert all(issubclass(c, Element) for c in elements)


@pytest.mark.parametrize("class_", all_presented_uml_and_sysml_elements())
def test_element_has_concrete_ownable_property(class_):
    owners = list(concrete_owner_property(class_))

    assert any(owners)
