"""
An item representing a diagram.
"""

import gaphor.UML.uml as UML
from gaphor.diagram.presentation import ElementPresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, IconBox, Text, draw_border, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.Diagram)
class DiagramItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=30, height=30)
        for h in self.handles():
            h.movable = False

        self.shape = IconBox(
            Box(
                Box(draw=draw_diagram),
                draw=draw_border,
            ),
            CssNode(
                "type",
                self.subject,
                Text(
                    text=lambda: self.subject and self.subject.diagramType or "",
                ),
            ),
            text_stereotypes(self),
            text_name(self),
        )

        self.watch("subject[UML:Diagram].name")
        self.watch("subject[Core:Diagram].diagramType")
        self.watch("subject[UML:Element].appliedStereotype.classifier.name")


def draw_diagram(box, context, bounding_box):
    cr = context.cairo

    cr.rectangle(5, 13, 8, 12)
    cr.rectangle(18, 5, 8, 12)
    cr.move_to(17, 9)
    cr.line_to(8, 9)
    cr.line_to(8, 12)
    stroke(context, fill=True)


for _type in (
    UML.ClassDiagram,
    UML.PackageDiagram,
    UML.ComponentDiagram,
    UML.DeploymentDiagram,
    UML.ActivityDiagram,
    UML.SequenceDiagram,
    UML.CommunicationDiagram,
    UML.StateMachineDiagram,
    UML.UseCaseDiagram,
    UML.ProfileDiagram,
):
    represents(_type)(DiagramItem)
