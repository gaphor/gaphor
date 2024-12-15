from gaphor.diagram.support import represents
from gaphor.SysML.sysml import (
    ActivityDiagram,
    BlockDefinitionDiagram,
    InternalBlockDiagram,
    PackageDiagram,
    RequirementDiagram,
    SequenceDiagram,
    StateMachineDiagram,
    UseCaseDiagram,
)
from gaphor.UML.general.diagramitem import DiagramItem

for _type in (
    ActivityDiagram,
    BlockDefinitionDiagram,
    InternalBlockDiagram,
    PackageDiagram,
    RequirementDiagram,
    SequenceDiagram,
    StateMachineDiagram,
    UseCaseDiagram,
):
    represents(_type)(DiagramItem)
