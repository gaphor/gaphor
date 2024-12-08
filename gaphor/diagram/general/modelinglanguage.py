"""Some general diagram items, including presentations for Core elements."""

from gaphor.abc import ModelingLanguage
from gaphor.diagram.general import diagramitems


class GeneralModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return ""

    @property
    def toolbox_definition(self):
        raise ValueError("No toolbox for the core model")

    @property
    def diagram_types(self):
        raise ValueError("No diagram types for the core model")

    @property
    def element_types(self):
        raise ValueError("No element types for the core model")

    @property
    def model_browser_model(self):
        raise ValueError("No model browser model for the core model")

    def lookup_element(self, name, ns=None):
        assert ns in ("general", None)
        return getattr(diagramitems, name, None)
