from typing import Dict, Iterable

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

    def __init__(self, event_manager=None, properties=None):
        """Create a new Model Provider. It will provide all models defined as
        entrypoints under `[gaphor.modelinglanguages]`.

        The `properties` argument is optional, in which case the service
        will default to UML.
        """
        if properties is None:
            properties = {}
        self.event_manager = event_manager
        self.properties = properties

        self._modeling_languages: Dict[str, ModelingLanguage] = initialize(
            "gaphor.modelinglanguages"
        )
        if event_manager:
            self.event_manager.subscribe(self.on_property_changed)

    def shutdown(self):
        if self.event_manager:
            self.event_manager.unsubscribe(self.on_property_changed)

    @property
    def modeling_languages(self) -> Iterable[tuple[str, str]]:
        """An Iterator, returns tuples (id, localized name)."""
        for id, provider in self._modeling_languages.items():
            if provider.name:
                yield id, provider.name

    @property
    def active_modeling_language(self) -> str:
        """The identifier for the currently active modeling language."""
        modeling_language: str = self.properties.get(
            "modeling-language", self.DEFAULT_LANGUAGE
        )
        if modeling_language not in self._modeling_languages:
            modeling_language = self.DEFAULT_LANGUAGE
        return modeling_language

    @property
    def name(self) -> str:
        """Localized name of the active modeling language."""
        return self._modeling_language().name

    @property
    def toolbox_definition(self):
        return self._modeling_language().toolbox_definition

    @property
    def diagram_types(self):
        return self._modeling_language().diagram_types

    @property
    def element_types(self):
        return self._modeling_language().element_types

    def lookup_element(self, name):
        return next(
            filter(
                None,
                [
                    provider.lookup_element(name)
                    for provider in self._modeling_languages.values()
                ],
            ),
            None,
        )

    @action(name="select-modeling-language")
    def select_modeling_language(self, modeling_language: str):
        self.properties.set("modeling-language", modeling_language)
        if self.event_manager:
            self.event_manager.handle(ModelingLanguageChanged(modeling_language))

    def _modeling_language(self) -> ModelingLanguage:
        return self._modeling_languages[self.active_modeling_language]

    @event_handler(PropertyChanged)
    def on_property_changed(self, event: PropertyChanged):
        if event.key == "modeling-language" and self.event_manager:
            self.event_manager.handle(ModelingLanguageChanged(event.new_value))
