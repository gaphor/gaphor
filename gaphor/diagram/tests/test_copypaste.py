import pytest

from gaphor.diagram.copypaste import copy, paste


def test_copy_unknown_type_raises_exception():
    with pytest.raises(ValueError):
        copy(None)


def test_paste_unknown_type_raises_exception(diagram, element_factory):
    with pytest.raises(ValueError):
        paste(None, diagram, element_factory.lookup)
