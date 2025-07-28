"""The Kernel Modeling Language module is the basis for SysML 2.x.

NB. The KerML modeling language does require the namespace to be present.
    This avoids name clashes with the UML model.
"""

from gaphor.abc import ModelingLanguage
from gaphor.KerML import kerml


class KerMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return ""

    @property
    def toolbox_definition(self):
        raise ValueError("No toolbox for the KerML model")

    @property
    def diagram_types(self):
        raise ValueError("No diagram types for the KerML model")

    @property
    def element_types(self):
        raise ValueError("No element types for the KerML model")

    @property
    def model_browser_model(self):
        raise ValueError("No model browser model for the KerML model")

    def lookup_element(self, name, ns=None):
        if ns == "KerML":
            return getattr(kerml, name)
        return None
