from typing import Dict

from gaphor.abc import ActionProvider, ModelProvider, Service
from gaphor.action import action, init_action_state
from gaphor.entrypoint import initialize
from gaphor.ui.event import ModelingLanguageChanged


class ModelProviderService(Service, ActionProvider, ModelProvider):

    DEFAULT_PROFILE = "UML"

    def __init__(self, event_manager, properties={}):
        """
        Create a new Model Provider. It will provide all models defined
        as entrypoints under `[gaphor.modelproviders]`.

        The `properties` argument is optional, in which case the service
        will default to UML.
        """
        self.event_manager = event_manager
        self.properties = properties

        self.model_providers: Dict[str, ModelProvider] = initialize(
            "gaphor.modelproviders"
        )

        init_action_state(
            ModelProviderService.action_select_modeling_language,
            self.active_modeling_language,
        )

    def shutdown(self):
        pass

    @property
    def modeling_languages(self):
        """
        A Generator, returns tuples (id, localized name).
        """
        for id, provider in self.model_providers.items():
            yield id, provider.name

    @property
    def active_modeling_language(self):
        modeling_language = self.properties.get(
            "modeling-language", self.DEFAULT_PROFILE
        )
        if modeling_language not in self.model_providers:
            modeling_language = self.DEFAULT_PROFILE
        return modeling_language

    @property
    def active_modeling_language_name(self):
        return self.model_providers[self.active_modeling_language].name

    @property
    def _modeling_language(self):
        return self.model_providers[self.active_modeling_language]

    @property
    def name(self):
        return self._modeling_language.name

    @property
    def toolbox_definition(self):
        return self._modeling_language.toolbox_definition

    def lookup_element(self, name):
        return self.first(lambda provider: provider.lookup_element(name))

    def lookup_diagram_item(self, name):
        return self.first(lambda provider: provider.lookup_diagram_item(name))

    def first(self, predicate):
        for _, provider in self.model_providers.items():
            type = predicate(provider)
            if type:
                return type

    @action(name="select-modeling-language", state=DEFAULT_PROFILE)
    def action_select_modeling_language(self, modeling_language: str):
        self.properties.set("modeling-language", modeling_language)
        self.event_manager.handle(ModelingLanguageChanged(modeling_language))
