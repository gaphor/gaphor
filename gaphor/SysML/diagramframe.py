from gaphor.diagram.presentation import (
    ElementPresentation,
    Framed,
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
from gaphor.UML.actions.activity import update_parameter_nodes
from gaphor.UML.recipes import stereotypes_str
from gaphor.UML.uml import Activity, Diagram, NamedElement


class DiagramFrameItem(Framed, ElementPresentation):
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

        self.watch("subject[UML:NamedElement].name").watch(
            "diagram[UML:Diagram].name"
        ).watch("diagram[UML:Diagram].element[UML:NamedElement].name").watch(
            "subject[UML:Activity].node", self.update_activity_parameters
        )

    def label(self):
        assert isinstance(self.diagram, Diagram)
        return diagram_label(self.diagram)

    def postload(self):
        super().postload()
        if isinstance(self.subject, Activity):
            self.update_activity_parameters()

    def update_activity_parameters(self, event=None):
        if not isinstance(self.subject, Activity):
            return

        update_parameter_nodes(self)


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
