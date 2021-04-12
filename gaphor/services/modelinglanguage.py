from typing import Dict

from gaphor.abc import ActionProvider, ModelingLanguage, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.entrypoint import initialize
from gaphor.services.properties import PropertyChanged


class ModelingLanguageChanged:
    def __init__(self, modeling_language):
        self.modeling_language = modeling_language


class ModelingLanguageService(Service, ActionProvider, ModelingLanguage):

    DEFAULT_LANGUAGE = "UML"

    def __init__(self, event_manager, properties={}):
        """Create a new Model Provider. It will provide all models defined as
        entrypoints under `[gaphor.modelinglanguages]`.

        The `properties` argument is optional, in which case the service
        will default to UML.
        """
        self.event_manager = event_manager
        self.properties = properties

        self._modeling_languages: Dict[str, ModelingLanguage] = initialize(
            "gaphor.modelinglanguages"
        )
        self.event_manager.subscribe(self.on_property_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_property_changed)

    @property
    def modeling_languages(self):
        """A Generator, returns tuples (id, localized name)."""
        for id, provider in self._modeling_languages.items():
            yield id, provider.name

    @property
    def active_modeling_language(self):
        modeling_language = self.properties.get(
            "modeling-language", self.DEFAULT_LANGUAGE
        )
        if modeling_language not in self._modeling_languages:
            modeling_language = self.DEFAULT_LANGUAGE
        return modeling_language

    @property
    def active_modeling_language_name(self):
        return self._modeling_languages[self.active_modeling_language].name

    @property
    def _modeling_language(self):
        return self._modeling_languages[self.active_modeling_language]

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
        for _, provider in self._modeling_languages.items():
            type = predicate(provider)
            if type:
                return type

    @action(
        name="select-modeling-language",
        state=lambda self: self.active_modeling_language,
    )
    def action_select_modeling_language(self, modeling_language: str):
        self.properties.set("modeling-language", modeling_language)
        self.event_manager.handle(ModelingLanguageChanged(modeling_language))

    @event_handler(PropertyChanged)
    def on_property_changed(self, event: PropertyChanged):
        if event.key == "modeling-language":
            self.event_manager.handle(ModelingLanguageChanged(event.new_value))
