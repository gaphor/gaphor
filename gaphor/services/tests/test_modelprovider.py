from gaphor.services.modelprovider import ModelProviderService


def test_loading_of_model_providers():
    model_provider = ModelProviderService(properties={})

    assert "UML" in model_provider.model_providers
