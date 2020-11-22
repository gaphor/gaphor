"""Activity Partition item."""

from typing import List

from cairo import Context as CairoContext
from gaphas.geometry import Rectangle
from generic.event import Event

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import Style, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, cairo_state, draw_highlight, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import Layout

INIT_NUM_PARTITIONS: int = 2


@represents(UML.ActivityPartition)
class PartitionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.partitions: List[UML.ActivityPartition] = []
        self.min_width = 150
        self.min_height = 300
        self.style: Style = {
            "font-family": "sans",
            "font-size": 14,
            "line-width": 2.4,
            "padding": (2, 2, 2, 2),
            "vertical-align": VerticalAlign.TOP,
        }

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("num_partitions", self.update_shapes)
        self.watch("partitions_dirty", self.update_shapes)

    num_partitions: attribute[int] = attribute(
        "num_partitions", int, default=INIT_NUM_PARTITIONS
    )
    partitions_dirty: attribute[bool] = attribute(
        "partitions_dirty", bool, default=False
    )

    def pre_update(self, context: DrawContext) -> None:
        """Set the min width of all the swimlanes."""
        self.min_width = 150 * self.num_partitions

    def post_update(self, context: DrawContext) -> None:
        """Nest the Activity Partitions under the Activity.

        This needs to be done after the update because the activity's
        classifier doesn't always exist yet.
        """
        activity = self.diagram.namespace
        for partition in self.partitions:
            if not partition.activity and isinstance(
                activity.ownedClassifier[0], UML.Activity
            ):
                partition.activity = activity.ownedClassifier[0]

    def update_partitions(self) -> None:
        """Add and remove UML.ActivityPartitions."""
        if not len(self.partitions):
            self.partitions.append(self.subject)

        if self.num_partitions > len(self.partitions):
            partition = self.subject.model.create(UML.ActivityPartition)
            partition.name = "NewActivityPartition"
            self.partitions.append(partition)
        elif self.num_partitions < len(self.partitions):
            partition = self.partitions[-1]
            partition.unlink()
            self.partitions.pop()

    def update_shapes(self, event: Event = None) -> None:
        """Update the number of partitions and draw them."""
        self.update_partitions()
        self.shape = Box(
            style=self.style,
            draw=self.draw_swimlanes,
        )
        self.partitions_dirty = False

    def draw_swimlanes(
        self, box: Box, context: DrawContext, bounding_box: Rectangle
    ) -> None:
        """Draw the vertical partitions as connected swimlanes.

        The partitions are open on the bottom. We divide the total size
        by the total number of partitions and space them evenly.
        """
        assert self.canvas

        cr = context.cairo
        cr.set_line_width(context.style["line-width"])
        header_h = self.draw_outline(bounding_box, cr)
        self.draw_partitions(bounding_box, context, header_h)
        stroke(context)
        self.draw_hover(bounding_box, context)

    def draw_hover(self, bounding_box: Rectangle, context: DrawContext):
        """Add dashed line on bottom of swimlanes when hovered."""
        if context.hovered or context.dropzone:
            cr = context.cairo
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                draw_highlight(context)
                cr.stroke()

    def draw_partitions(
        self, bounding_box: Rectangle, context: DrawContext, header_h: int
    ) -> None:
        """Draw partition separators and add the name."""
        cr = context.cairo
        partition_width = bounding_box.width / self.num_partitions
        layout = Layout()
        padding_top = context.style["padding"][0]
        for num, partition in enumerate(self.partitions):
            cr.move_to(partition_width * num, 0)
            cr.line_to(partition_width * num, bounding_box.height)
            layout.set(text=partition.name, font=self.style)
            cr.move_to(partition_width * num, padding_top * 3)
            layout.show_layout(
                cr,
                partition_width,
                default_size=(partition_width, header_h),
            )

    def draw_outline(self, bounding_box: Rectangle, cr: CairoContext) -> int:
        """Draw the outline and header of the swimlanes."""
        cr.move_to(0, bounding_box.height)
        cr.line_to(0, 0)
        cr.line_to(bounding_box.width, 0)
        cr.line_to(bounding_box.width, bounding_box.height)
        cr.move_to(0, bounding_box.height)
        header_h = 29
        cr.line_to(0, header_h)
        cr.line_to(0 + bounding_box.width, header_h)
        cr.line_to(0 + bounding_box.width, bounding_box.height)
        return header_h
