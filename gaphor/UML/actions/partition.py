"""Activity Partition item."""

from typing import List

from gaphas.geometry import Rectangle

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import Style, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, cairo_state, draw_highlight, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import Layout


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
        self.watch("update_partition", self.update_shapes)

    num_partitions: attribute[int] = attribute("num_partitions", int, default=2)
    update_partition: attribute[bool] = attribute(
        "update_partition", bool, default=False
    )

    def pre_update(self, context):
        assert self.canvas
        if not len(self.partitions):
            self.partitions.append(self.subject)

        if self.num_partitions > len(self.partitions):
            package = self.diagram.namespace
            partition = self.subject.model.create(UML.ActivityPartition)
            partition.name = "NewActivityPartition"

            if isinstance(package.ownedClassifier[0], UML.Activity):
                activity = package.ownedClassifier[0]
                partition.activity = activity
            self.partitions.append(partition)

        elif self.num_partitions < len(self.partitions):
            partition = self.partitions[-1]
            partition.unlink()
            self.partitions.pop()

        self.min_width = 150 * self.num_partitions

    def update_shapes(self, event=None):
        self.shape = Box(
            style=self.style,
            draw=self.draw_partitions,
        )
        self.update_partition = False

    def draw_partitions(self, box: Box, context: DrawContext, bounding_box: Rectangle):
        """Draw a vertical partition.

        The partitions are open on the bottom.
        """
        assert self.canvas

        cr = context.cairo
        cr.set_line_width(context.style["line-width"])

        # Header left, top, and right outline
        cr.move_to(0, bounding_box.height)
        cr.line_to(0, 0)
        cr.line_to(bounding_box.width, 0)
        cr.line_to(bounding_box.width, bounding_box.height)

        # Header bottom outline
        cr.move_to(0, bounding_box.height)
        header_h = 29
        cr.line_to(0, header_h)
        cr.line_to(0 + bounding_box.width, header_h)
        cr.line_to(0 + bounding_box.width, bounding_box.height)

        partition_width = bounding_box.width / self.num_partitions
        layout = Layout()

        for num, partition in enumerate(self.partitions):
            # Draw partition separators
            cr.move_to(partition_width * num, 0)
            cr.line_to(partition_width * num, bounding_box.height)

            if partition:
                # Add the name to child partition
                layout.set(text=partition.name, font=self.style)
                padding_top = context.style["padding"][0]
                cr = context.cairo
                cr.move_to(partition_width * num, padding_top * 3)
                layout.show_layout(
                    cr,
                    partition_width,
                    default_size=(partition_width, header_h),
                )

        stroke(context)

        if context.hovered or context.dropzone:
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                draw_highlight(context)
                cr.stroke()
