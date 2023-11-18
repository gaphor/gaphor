from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext, UpdateContext
from gaphor.core.styling import (
    FontWeight,
    TextAlign,
)
from gaphor.diagram.deletable import item_explicitly_deletable
from gaphor.diagram.diagramlabel import diagram_label
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    connect,
)
from gaphor.diagram.shapes import (
    cairo_state,
)
from gaphor.diagram.text import Layout
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.uml import Activity, ActivityParameterNode


class DiagramFrameItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("diagram[Diagram].name", self.update_shapes).watch(
            "diagram[Diagram].diagramType", self.update_shapes
        ).watch("diagram[Diagram].element", self.update_element).watch(
            "subject", self.update_element
        ).watch("subject[Activity].node", self.update_frame_attachments).watch(
            "diagram[Diagram].element[NamedElement].name", self.update_shapes
        )

    def update_element(self, event=None):
        if not self.diagram or not self.diagram.element:
            return

        self.subject = self.diagram.element
        self.update_shapes()
        self.update_frame_attachments()

    def postload(self):
        super().postload()
        self.update_frame_attachments()

    def update_shapes(self, event=None):
        if not self.diagram:
            return

        self.shape = DiagramFrameShape(
            kind=self.diagram.diagramType,
            label=diagram_label(self.diagram),
        )

    def update_frame_attachments(self, event=None):
        if not self.subject:
            return

        if isinstance(self.subject, Activity):
            self.update_activity_parameters()

    def update_activity_parameters(self):
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


class DiagramFrameShape:
    def __init__(self, kind: str, label: str):
        self._kind_layout = self._create_layout(kind, FontWeight.BOLD)
        self._label_layout = self._create_layout(f" {label}", FontWeight.NORMAL)

        self._kind_size = self._kind_layout.size()
        self._label_size = self._label_layout.size()
        self._margin = 5

    def _create_layout(self, text: str, font_weight: FontWeight):
        layout = Layout()
        layout.set(
            text=text,
            font={
                "font-weight": font_weight,
                "text-align": TextAlign.LEFT,
                "font-family": "sans",
                "font-size": 12,
            },
        )

        return layout

    def size(self, context: UpdateContext):
        kind_w, kind_h = self._kind_size
        label_w, label_h = self._label_size

        self._header_width = 2 * self._margin + kind_w + label_w
        self._header_height = 2 * self._margin + max(kind_h, label_h)

        width = self._header_width + 30
        height = self._header_height + 50

        return width, height

    def draw(self, context: DrawContext, bounding_box: Rectangle):
        cr = context.cairo
        x, y, width, height = bounding_box

        cr.set_dash((), 0)
        cr.rectangle(x, y, width, height)
        cr.move_to(x, y + self._header_height)
        cr.line_to(x + self._header_width, y + self._header_height)
        cr.line_to(x + self._header_width + 10, y + self._header_height - 10)
        cr.line_to(x + self._header_width + 10, y)
        cr.line_to(x, y)
        cr.close_path()

        with cairo_state(context.cairo) as cr:
            if text_color := context.style.get("text-color"):
                cr.set_source_rgba(*text_color)

            cr.move_to(x + self._margin, y + self._margin)
            w, _ = self._kind_size
            self._kind_layout.show_layout(cr, w, default_size=(w, self._header_height))

            cr.move_to(x + self._margin + w, y + self._margin)
            w, _ = self._label_size
            self._label_layout.show_layout(cr, w, default_size=(w, self._header_height))

        cr.stroke()


@item_explicitly_deletable.register
def diagram_frame_item_explicitly_deletable(item: DiagramFrameItem):
    return False
