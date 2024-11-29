import contextlib

import pytest

import gaphor.C4Model.diagramitems as C4Model_diagramitems
import gaphor.RAAML.diagramitems as RAAML_diagramitems
import gaphor.SysML.diagramitems as SysML_diagramitems
import gaphor.UML.diagramitems as UML_diagramitems
from gaphor.core.modeling import Element
from gaphor.core.modeling.properties import umlproperty


def presentations(module):
    for name in dir(module):
        element_type = getattr(module, name)
        with contextlib.suppress(TypeError):
            if issubclass(element_type, Element):
                yield element_type


def flatten(list):
    return [item for sublist in list for item in sublist]


@pytest.mark.parametrize(
    "element_type",
    set(
        flatten(
            [
                presentations(UML_diagramitems),
                presentations(SysML_diagramitems),
                presentations(C4Model_diagramitems),
                presentations(RAAML_diagramitems),
            ]
        )
    ),
)
def test_property_name(element_type):
    for name in dir(element_type):
        if name.startswith("GAPHOR__"):
            continue
        prop = getattr(element_type, name)
        if isinstance(prop, umlproperty):
            assert (
                name == prop.name
            ), f"No matching property name for {element_type}.{name}"
