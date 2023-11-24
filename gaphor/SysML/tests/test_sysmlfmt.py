import pytest

from gaphor.core.format import format
from gaphor.SysML import sysml

TYPES = [sysml.Allocate, sysml.Refine, sysml.Trace]


@pytest.mark.parametrize("type", TYPES)
def test_format_simple_property_path(type):
    rel = type()

    assert format(rel) == "sourceContext: "


@pytest.mark.parametrize("type", TYPES)
def test_format_connected_property_path(type):
    block = sysml.Block()
    block.name = "MyBlock"

    rel = type()
    rel.sourceContext = block

    assert format(rel) == "sourceContext: MyBlock"
