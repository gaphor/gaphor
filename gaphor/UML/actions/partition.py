"""Activity Partition item."""

from typing import List

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, cairo_state, draw_highlight, stroke
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.ActivityPartition)
class PartitionItem(ElementPresentation, Named):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.children: List[UML.ActivityPartition] = []
        self.min_width = 150
        self.min_height = 300

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("num_partitions", self.update_shapes)

    num_partitions: attribute[int] = attribute("num_partitions", int, default=2)

    def pre_update(self, context):
        assert self.canvas

        while (self.num_partitions - 1) > len(self.children):
            package = self.diagram.namespace
            partition = self.subject.model.create(UML.ActivityPartition)

            if isinstance(package.ownedClassifier[0], UML.Activity):
                activity = package.ownedClassifier[0]
                partition.activity = activity
            self.children.append(partition)

        while (self.num_partitions - 1) < len(self.children):
            partition = self.children[-1]
            partition.unlink()
            self.children.pop()

    def update_shapes(self, event=None):
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(
                    self.subject,
                    self.subject and self.subject.isExternal and ("external",) or (),
                ),
            ),
            Text(text=lambda: self.subject.name or ""),
            style={
                "min-width": 0,
                "min-height": 0,
                "line-width": 2.4,
                "vertical-align": VerticalAlign.TOP,
                "padding": (2, 2, 2, 2),
            },
            draw=self.draw_swim_lanes,
        )

    def draw_partition(self, context, bounding_box, x_offset):
        """Draw a vertical partition.

        The partitions are open on the bottom.
        """
        assert self.canvas

        cr = context.cairo
        cr.set_line_width(context.style["line-width"])

        # Header left, top, and right outline
        cr.move_to(x_offset, bounding_box.height)
        cr.line_to(x_offset, 0)
        cr.line_to(x_offset + bounding_box.width, 0)
        cr.line_to(x_offset + bounding_box.width, bounding_box.height)

        # Header bottom outline
        cr.move_to(x_offset, bounding_box.height)
        h = self.shape.size(context)[1]
        cr.line_to(x_offset, h)
        cr.line_to(x_offset + bounding_box.width, h)
        cr.line_to(x_offset + bounding_box.width, bounding_box.height)

        stroke(context)

        if context.hovered or context.dropzone:
            with cairo_state(cr):
                cr.set_dash((1.0, 5.0), 0)
                cr.set_line_width(1.0)
                cr.rectangle(0, 0, bounding_box.width, bounding_box.height)
                draw_highlight(context)
                cr.stroke()

    def draw_swim_lanes(self, box, context, bounding_box):
        """Draw the partitions in parallel swim lanes."""
        self.draw_partition(context, bounding_box, 0)
        for num, _ in enumerate(self.children, start=1):
            self.draw_partition(context, bounding_box, bounding_box.width * num)
