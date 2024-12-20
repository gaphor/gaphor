from gaphor.diagram.painter import DiagramTypePainter
from gaphor.SysML.diagramframe import DiagramFrameItem, diagram_label
from gaphor.SysML.sysml import SysMLDiagram
from gaphor.UML.painter import UMLDiagramTypePainter


@DiagramTypePainter.register(SysMLDiagram)  # type: ignore[attr-defined]
class SysMLDiagramTypePainter(UMLDiagramTypePainter):
    def label(self):
        return diagram_label(self.diagram)

    def paint(self, items, cr):
        if any(isinstance(p, DiagramFrameItem) for p in self.diagram.ownedPresentation):
            return

        super().paint(items, cr)
