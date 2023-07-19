"""The SysML Modeling Language module is the entrypoint for SysML related
assets."""

from typing import Iterable

from gaphor.abc import ModelingLanguage
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import DiagramType, ToolboxDefinition
from gaphor.SysML import diagramitems, sysml
from gaphor.SysML.toolbox import sysml_diagram_types, sysml_toolbox_actions
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement
from gaphor.UML.uml import Activity, Interaction, Package, Profile, StateMachine


class SysMLModelingLanguage(ModelingLanguage):
    @property
    def name(self) -> str:
        return gettext("SysML")

    @property
    def toolbox_definition(self) -> ToolboxDefinition:
        return sysml_toolbox_actions

    @property
    def diagram_types(self) -> Iterable[DiagramType]:
        yield from sysml_diagram_types

    def lookup_element(self, name):
        return getattr(sysml, name, None) or getattr(diagramitems, name, None)

    def format_diagram_label(self, diagram) -> str:
        if not diagram.element:
            # The diagram is created under the root
            return str(diagram.name)

        options = [
            ("activity", Activity),
            (
                "constraint block",
                ConstraintBlock,
            ),  # Must be before block, because constraint block is derived from block
            ("block", Block),
            ("interaction", Interaction),
            (
                "profile",
                Profile,
            ),  # Must be before package, because profile is derived from package
            ("package", Package),
            ("requirement", Requirement),
            ("state machine", StateMachine),
        ]

        model_element_type = next(
            name for name, kind in options if isinstance(diagram.element, kind)
        )
        model_element_name = diagram.element.name or ""

        return f"[{model_element_type}] {model_element_name} [{diagram.name}]"
