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

    def lookup_element(self, name):
        return getattr(coremodel, name, None)
