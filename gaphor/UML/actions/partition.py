"""Activity Partition item."""

from gaphas.geometry import Rectangle

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import association
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, stroke
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
                "padding": (4, 12, 4, 12),
                "vertical-align": VerticalAlign.TOP,
            },
            draw=self.draw_swimlanes,
        )
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("partition", self.update_partition)
        self.watch("partition.name")
        self.watch("partition[ActivityPartition].represents[NamedElement].name")

    partition = association("partition", UML.ActivityPartition, composite=True)

    def postload(self):
        super().postload()
        if self.subject and self.subject not in self.partition:
            self.partition = self.subject

    def update_partition(self, context: DrawContext) -> None:
        """Set the min width of all the swimlanes."""
        self.min_width = 150 * len(self.partition)
        self.request_update()

    def draw_swimlanes(
        self, box: Box, context: DrawContext, bounding_box: Rectangle
    ) -> None:
        """Draw the vertical partitions as connected swimlanes.

        The partitions are open on the bottom. We divide the total size
        by the total number of partitions and space them evenly.
        """
        cr = context.cairo
        cr.set_line_width(context.style["line-width"])
        partitions = self.partition

        if partitions:
            partition_width = bounding_box.width / len(partitions)
        else:
            partition_width = bounding_box.width / 2

        padding_top, padding_right, padding_bottom, padding_left = context.style[
            "padding"
        ]
        layout = Layout(
            font=context.style,
            width=partition_width - padding_left - padding_right,
        )
        header_height = 0.0
        for num, partition in enumerate(partitions):
            cr.move_to(partition_width * num, 0)
            cr.line_to(partition_width * num, bounding_box.height)
            layout.set(
                text=f"{partition.name}: {partition.represents.name}"
                if isinstance(partition.represents, UML.NamedElement)
                else partition.name
            )
            cr.move_to(partition_width * num + padding_left, padding_top)
            layout.show_layout(cr)
            _, h = layout.size()
            header_height = max(h, header_height)

        cr.move_to(bounding_box.width, 0)
        cr.line_to(bounding_box.width, bounding_box.height)

        header_height += padding_top + padding_bottom
        cr.move_to(0, 0)
        cr.line_to(0 + bounding_box.width, 0)
        cr.move_to(0, header_height)
        cr.line_to(0 + bounding_box.width, header_height)
        stroke(context)
