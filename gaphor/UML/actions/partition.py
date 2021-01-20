"""Activity Partition item."""

from gaphas.geometry import Rectangle

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import association
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, cairo_state, draw_highlight, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import Layout

HEADER_HEIGHT: int = 29


@represents(UML.ActivityPartition)
class PartitionItem(ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.min_height = 300

        self.shape = Box(
            style={
                "line-width": 2.4,
                "padding": (2, 2, 2, 2),
                "vertical-align": VerticalAlign.TOP,
            },
            draw=self.draw_swimlanes,
        )
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("partition.name")
        self.watch("partition")

    partition = association("partition", UML.ActivityPartition, composite=True)

    def postload(self):
        super().postload()
        if self.subject and self.subject not in self.partition:
            self.partition = self.subject

    def pre_update(self, context: DrawContext) -> None:
        """Set the min width of all the swimlanes."""
        self.min_width = 150 * len(self.partition)

    def draw_swimlanes(
        self, box: Box, context: DrawContext, bounding_box: Rectangle
    ) -> None:
        """Draw the vertical partitions as connected swimlanes.

        The partitions are open on the bottom. We divide the total size
        by the total number of partitions and space them evenly.
        """
        cr = context.cairo
        cr.set_line_width(context.style["line-width"])
        self.draw_outline(bounding_box, context)
        self.draw_partitions(bounding_box, context)
        stroke(context)
        self.draw_hover(bounding_box, context)

    def draw_hover(self, bounding_box: Rectangle, context: DrawContext) -> None:
        """Add dashed line on bottom of swimlanes when hovered."""
        if context.hovered or context.dropzone:
            cr = context.cairo
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                cr.stroke()

    def draw_partitions(self, bounding_box: Rectangle, context: DrawContext) -> None:
        """Draw partition separators and add the name."""
        cr = context.cairo
        if self.partition:
            partition_width = bounding_box.width / len(self.partition)
        else:
            partition_width = bounding_box.width / 2
        layout = Layout()
        style = context.style
        padding_top = context.style["padding"][0]
        for num, partition in enumerate(self.partition):
            cr.move_to(partition_width * num, 0)
            cr.line_to(partition_width * num, bounding_box.height)
            layout.set(text=partition.name, font=style)
            cr.move_to(partition_width * num, padding_top * 3)
            layout.show_layout(
                cr,
                partition_width,
                default_size=(partition_width, HEADER_HEIGHT),
            )

    def draw_outline(self, bounding_box: Rectangle, context: DrawContext) -> None:
        """Draw the outline and header of the swimlanes."""
        cr = context.cairo
        cr.move_to(0, bounding_box.height)
        cr.line_to(0, 0)
        cr.line_to(bounding_box.width, 0)
        cr.line_to(bounding_box.width, bounding_box.height)
        draw_highlight(context)
        cr.move_to(0, bounding_box.height)
        cr.line_to(0, HEADER_HEIGHT)
        cr.line_to(0 + bounding_box.width, HEADER_HEIGHT)
        cr.line_to(0 + bounding_box.width, bounding_box.height)
