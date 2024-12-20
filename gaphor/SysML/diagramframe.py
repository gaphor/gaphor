from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    connect,
)
from gaphor.diagram.shapes import (
    DEFAULT_PADDING,
    Box,
    CssNode,
    Orientation,
    Text,
    cairo_state,
    draw_border,
    stroke,
)
from gaphor.SysML.sysml import Block, ConstraintBlock, Requirement
from gaphor.UML import Interaction, Package, Profile, StateMachine
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.recipes import stereotypes_str
from gaphor.UML.uml import Activity, ActivityParameterNode, Diagram, NamedElement


class DiagramFrameItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape=Box(
                Box(
                    CssNode(
                        "pentagon",
                        self,
                        Box(
                            CssNode(
                                "diagramtype",
                                None,
                                Text(text=lambda: self.diagram.diagramType),
                            ),
                            CssNode(
                                "stereotypes",
                                None,
                                Text(text=lambda: stereotypes_str(diagram)),
                            ),
                            CssNode("name", None, Text(text=self.label)),
                            orientation=Orientation.HORIZONTAL,
                            draw=draw_pentagon,
                        ),
                    )
                ),
                draw=draw_border,
            ),
        )

        self.watch("subject", self.update_element).watch(
            "diagram[UML:Diagram].name", self.update_shapes
        ).watch(
            "diagram[UML:Diagram].element[UML:NamedElement].name", self.update_shapes
        ).watch("subject[UML:Activity].node", self.update_frame_attachments)

    def label(self):
        assert isinstance(self.diagram, Diagram)
        return diagram_label(self.diagram)

    def update_element(self, event=None):
        assert isinstance(self.diagram, Diagram)
        if not self.diagram or not self.diagram.element:
            return

        self.subject = self.diagram.element
        self.update_shapes()
        self.update_frame_attachments()

    def postload(self):
        super().postload()
        self.update_frame_attachments()

    def update_frame_attachments(self, event=None):
        if not self.subject:
            return

        if isinstance(self.subject, Activity):
            self.update_activity_parameters()

    def update_activity_parameters(self):
        assert isinstance(self.diagram, Diagram)
        assert self.diagram.element == self.subject
        assert isinstance(self.subject, Activity)

        diagram = self.diagram
        subject = self.subject

        assert isinstance(subject, Activity)

        parameter_nodes = (
            [p for p in subject.node if isinstance(p, ActivityParameterNode)]
            if subject
            else []
        )
        parameter_items = {
            i.subject: i
            for i in self.children
            if isinstance(i, ActivityParameterNodeItem)
        }

        for node in parameter_nodes:
            if node not in parameter_items:
                item = diagram.create(
                    ActivityParameterNodeItem, parent=self, subject=node
                )
                item.matrix.translate(0, 10)
                connect(item, item.handles()[0], self)

        for node in parameter_items:
            if node not in parameter_nodes:
                del self.children[parameter_items[node]]


def draw_pentagon(box, context, _bounding_box):
    cr = context.cairo
    _padding_top, _padding_right, padding_bottom, padding_left = context.style.get(
        "padding", DEFAULT_PADDING
    )
    w = sum(x for x, _y in box.sizes) + padding_left
    h = max(y for _x, y in box.sizes) + padding_bottom

    with cairo_state(cr):
        h2 = h / 2.0
        cr.move_to(0, h)
        cr.line_to(w - 4, h)
        cr.line_to(w, h2)
        cr.line_to(w, 0)
        stroke(context, fill=False)


def diagram_label(diagram):
    if (el := diagram.element) and isinstance(el, NamedElement):
        return f"[{_model_element_type(el)}] {el.name} [{diagram.name}]"

    # TODO: SysML specification does not allow parentless elements,
    #       but since it is not constrained (yet), it may happen.
    return diagram.name


def _model_element_type(el) -> str:
    if isinstance(el, Activity):
        return "activity"
    if isinstance(el, ConstraintBlock):
        return "constraint block"
    if isinstance(el, Block):
        return "block"
    if isinstance(el, Interaction):
        return "interaction"
    if isinstance(el, Profile):
        return "profile"
    if isinstance(el, Package):
        return "package"
    if isinstance(el, Requirement):
        return "requirement"
    return "state machine" if isinstance(el, StateMachine) else ""
