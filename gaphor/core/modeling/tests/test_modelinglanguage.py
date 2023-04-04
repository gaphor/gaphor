import pytest

from gaphor.core.modeling.modelinglanguage import CoreModelingLanguage


def test_name():
    modeling_language = CoreModelingLanguage()

    assert modeling_language.name == ""


def test_lookup_element():
    modeling_language = CoreModelingLanguage()

    assert modeling_language.lookup_element("Diagram")
    assert modeling_language.lookup_element("Element")
    assert modeling_language.lookup_element("Comment")
    assert modeling_language.lookup_element("Presentation")
    assert modeling_language.lookup_element("StyleSheet")
    assert not modeling_language.lookup_element("NonExistent")


def test_toolbox():
    modeling_language = CoreModelingLanguage()

    with pytest.raises(ValueError):
        modeling_language.toolbox_definition  # noqa: B018
