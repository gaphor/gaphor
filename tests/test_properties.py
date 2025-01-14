import contextlib

import pytest

import gaphor.C4Model.diagramitems
import gaphor.diagram.general.diagramitems
import gaphor.RAAML.diagramitems
import gaphor.SysML.diagramitems
import gaphor.UML.diagramitems
from gaphor.core.modeling import Base
from gaphor.core.modeling.properties import umlproperty


def presentations(module):
    for name in dir(module):
        element_type = getattr(module, name)
        with contextlib.suppress(TypeError):
            if issubclass(element_type, Base):
                yield element_type


def flatten(list):
    return [item for sublist in list for item in sublist]


def test_extract_presentations():
    assert list(presentations(gaphor.UML.diagramitems))


@pytest.mark.parametrize(
    "element_type",
    set(
        flatten(
            [
                presentations(gaphor.diagram.general.diagramitems),
                presentations(gaphor.UML.diagramitems),
                presentations(gaphor.SysML.diagramitems),
                presentations(gaphor.C4Model.diagramitems),
                presentations(gaphor.RAAML.diagramitems),
            ]
        )
    ),
)
def test_property_name_matches_assigned_name(element_type):
    for name in dir(element_type):
        prop = getattr(element_type, name)
        if isinstance(prop, umlproperty):
            assert name == prop.name, (
                f"No matching property name for {element_type}.{name}"
            )
