from gaphor.services.modelinglanguage import ModelingLanguageService


def test_loading_of_modeling_languages():
    modeling_language = ModelingLanguageService(event_manager=None, properties={})
    ids = [id for id, name in modeling_language.modeling_languages]
    assert "UML" in ids
