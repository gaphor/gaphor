from gaphor.services.modelinglanguage import ModelingLanguageService


def test_loading_of_modeling_languages(event_manager):
    modeling_language = ModelingLanguageService(
        event_manager=event_manager, properties={}
    )
    ids = [id for id, name in modeling_language.modeling_languages]
    assert "UML" in ids
