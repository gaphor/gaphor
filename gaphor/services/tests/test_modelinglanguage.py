import pytest

from gaphor.services.modelinglanguage import ModelingLanguageService


@pytest.fixture
def modeling_language(event_manager):
    return ModelingLanguageService(event_manager=event_manager, properties={})


def test_loading_of_modeling_languages(modeling_language):
    ids = [id for id, name in modeling_language.modeling_languages]
    assert "UML" in ids


def test_lookup_uml_element(modeling_language):
    assert modeling_language.lookup_element("Class")


def test_lookup_sysml_element(modeling_language):
    assert modeling_language.lookup_element("Block")


def test_lookup_c4model_element(modeling_language):
    assert modeling_language.lookup_element("C4Database")
