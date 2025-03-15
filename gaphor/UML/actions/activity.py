from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    AttachedPresentation,
    Classified,
    ElementPresentation,
    connect,
    text_name,
)
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.uml import Activity, ActivityParameterNode


@represents(Activity)
class ActivityItem(Classified, ElementPresentation[Activity]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=50)

        self.width = 100

        self.watch("subject[NamedElement].name").watch(
            "subject[Element].appliedStereotype.classifier.name"
        ).watch("subject[Classifier].isAbstract", self.update_shapes).watch(
            "subject[Activity].node[ActivityParameterNode].parameter",
            self.update_parameters,
        )

    def postload(self):
        super().postload()
        self.update_parameters()

    def update_shapes(self, event=None):
        self.shape = Box(
            text_stereotypes(self),
            text_name(self),
            draw=draw_border,
        )

    def update_parameters(self, event=None):
        update_parameter_nodes(self)


def update_parameter_nodes(item: ActivityItem):
    diagram = item.diagram
    subject = item.subject

    parameter_nodes = (
        [p for p in subject.node if isinstance(p, ActivityParameterNode)]
        if subject
        else []
    )
    parameter_items = {
        i.subject: i for i in item.children if isinstance(i, ActivityParameterNodeItem)
    }

    for node in parameter_nodes:
        if node not in parameter_items:
            node_item = diagram.create(
                ActivityParameterNodeItem, parent=item, subject=node
            )
            node_item.matrix.translate(0, 10)
            connect(node_item, node_item.handles()[0], item)

    for node in parameter_items:
        if node not in parameter_nodes:
            del item.children[parameter_items[node]]


@represents(ActivityParameterNode)
class ActivityParameterNodeItem(AttachedPresentation[ActivityParameterNode]):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape=Box(
                CssNode(
                    "name",
                    None,
                    Text(
                        text=self._format_name,
                    ),
                ),
                draw=draw_border,
            ),
        )

        self.watch("subject[ActivityParameterNode].parameter.name").watch(
            "subject[ActivityParameterNode].parameter.type.name"
        ).watch("subject[ActivityParameterNode].parameter.direction").watch(
            "show_type"
        ).watch("show_direction")

    show_type: attribute[int] = attribute("show_type", int, default=False)
    show_direction: attribute[int] = attribute("show_direction", int, default=False)

    def update(self, context):
        self.width, self.height = super().update(context)

    def _format_name(self):
        if not (self.subject and self.subject.parameter):
            return ""
        parameter = self.subject.parameter
        name = parameter.name or ""
        type = (parameter.type.name) if self.show_type and parameter.type else None
        direction = parameter.direction if self.show_direction else None

        if type and direction:
            return f"{direction} {name}: {type}"
        elif type:
            return f"{name}: {type}"
        elif direction:
            return f"{direction} {name}"
        return name
