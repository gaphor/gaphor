import pytest

from gaphor.diagram.general.modelinglanguage import GeneralModelingLanguage


def test_name():
    modeling_language = GeneralModelingLanguage()

    assert modeling_language.name == ""


def test_lookup_element():
    modeling_language = GeneralModelingLanguage()

    assert modeling_language.lookup_element("Box")
    assert modeling_language.lookup_element("Line")
    assert modeling_language.lookup_element("Ellipse")
    assert modeling_language.lookup_element("MetadataItem")


def test_toolbox():
    modeling_language = GeneralModelingLanguage()

    with pytest.raises(ValueError):
        modeling_language.toolbox_definition  # noqa: B018
