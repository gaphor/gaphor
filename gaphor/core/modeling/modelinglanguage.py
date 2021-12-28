"""C4 Model Language entrypoint."""

from gaphor.abc import ModelingLanguage
from gaphor.core.modeling import coremodel


class CoreModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return ""

    @property
    def toolbox_definition(self):
        raise ValueError("No toolbox for the core model")

    @property
    def diagram_types(self):
        raise ValueError("No diagram types for the core model")

    def lookup_element(self, name):
        return getattr(coremodel, name, None)


class MockModelingLanguage(ModelingLanguage):
    """This class can be used to instantly combine modeling languages."""

    def __init__(self, *modeling_languages: ModelingLanguage):
        self._modeling_languages = modeling_languages

    @property
    def name(self) -> str:
        return "Mock"

    @property
    def toolbox_definition(self):
        raise ValueError("No toolbox for the mock model")

    @property
    def diagram_types(self):
        raise ValueError("No diagram types for the mock model")

    def lookup_element(self, name):
        return next(
            filter(
                None,
                map(
                    lambda provider: provider.lookup_element(name),
                    self._modeling_languages,
                ),
            ),
            None,
        )
