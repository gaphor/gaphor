"""
Association item - graphical representation of an association.

Plan:
 - transform AssociationEnd in a (dumb) data class
 - for association name and direction tag, use the same trick as is used
   for line ends.
"""

from dataclasses import replace
from math import pi
from typing import Optional

from gaphas.connector import Handle
from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor import UML
from gaphor.core.modeling import DrawContext, UpdateContext
from gaphor.core.modeling.properties import association, attribute, enumeration
from gaphor.diagram.presentation import (
    LinePresentation,
    Named,
    get_center_pos,
    text_name,
)
from gaphor.diagram.shapes import (
    DEFAULT_PADDING,
    Box,
    CssNode,
    Number,
    Text,
    cairo_state,
    draw_default_head,
    draw_default_tail,
    stroke,
)
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.informationflow import (
    draw_information_flow,
    shape_information_flow,
    watch_information_flow,
)
from gaphor.UML.umlfmt import format_association_end

half_pi = pi / 2


@represents(UML.Association)
class AssociationItem(Named, LinePresentation[UML.Association]):
    """AssociationItem represents associations.

    An AssociationItem has two AssociationEnd items. Each AssociationEnd
    item represents a Property (with Property.association == my
    association).
    """

    def __init__(self, diagram, id=None):
        # AssociationEnds are really inseparable from the AssociationItem.
        self._head_end = AssociationEnd(owner=self, end="head")
        self._tail_end = AssociationEnd(owner=self, end="tail")

        super().__init__(
            diagram,
            id,
            shape_head=CssNode("end", None, self._head_end),
            shape_middle=Box(
                text_stereotypes(self),
                text_name(self),
                *shape_information_flow(self, "abstraction"),
            ),
            shape_tail=CssNode("end", None, self._tail_end),
        )

        # For the association ends:
        base = "subject[Association].memberEnd[Property]"
        self.watch("subject.name").watch(
            "subject.appliedStereotype.classifier.name"
        ).watch(f"{base}.name").watch(
            f"{base}.appliedStereotype.slot.definingFeature.name",
        ).watch(f"{base}.appliedStereotype.slot.value").watch(
            f"{base}.classifier"
        ).watch(f"{base}.visibility").watch(f"{base}.lowerValue").watch(
            f"{base}.upperValue"
        ).watch(f"{base}.owningAssociation").watch(
            f"{base}.type[Class].ownedAttribute"
        ).watch(f"{base}.type[Interface].ownedAttribute").watch(
            f"{base}.appliedStereotype.classifier"
        ).watch("subject[Association].memberEnd").watch("show_direction").watch(
            "preferred_tail_navigability"
        ).watch("preferred_aggregation", self.on_association_end_endings).watch(
            f"{base}.aggregation", self.on_association_end_endings
        ).watch(
            "subject[Association].navigableOwnedEnd", self.on_association_end_endings
        ).watch("subject[Association].ownedEnd", self.on_association_end_endings)

        # For types, see the Association.navigability override
        for t in [UML.Class, UML.DataType, UML.Interface]:
            self.watch(
                f"subject[Association].memberEnd.type[{t.__name__}].ownedAttribute",
                self.on_association_end_endings,
            )

        watch_information_flow(self, "Association", "abstraction")

    head_subject = association("head_subject", UML.Property, upper=1)
    tail_subject = association("tail_subject", UML.Property, upper=1)

    show_direction: attribute[int] = attribute("show_direction", int, default=False)

    preferred_aggregation = enumeration(
        "preferred_aggregation", ("none", "shared", "composite"), "none"
    )

    preferred_tail_navigability = enumeration(
        "preferred_tail_navigability", ("none", "navigable"), "none"
    )

    @property
    def head_end(self):
        return self._head_end

    @property
    def tail_end(self):
        return self._tail_end

    def load(self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ("head_end", "head-subject"):
            name = "head_subject"
        elif name in ("tail_end", "tail-subject"):
            name = "tail_subject"
        elif name == "show-direction":
            name = "show_direction"

        super().load(name, value)

    def postload(self):
        super().postload()
        self.on_association_end_endings()

    def invert_direction(self):
        """Invert the direction of the association, this is done by swapping
        the head and tail-ends subjects."""
        if not self.subject:
            return

        self.subject.memberEnd.swap(
            self.subject.memberEnd[0], self.subject.memberEnd[1]
        )
        self.request_update()

    def on_association_end_endings(self, event=None):
        head_subject = self.head_subject
        tail_subject = self.tail_subject

        # Update line ends using the aggregation and isNavigable values:
        if head_subject and tail_subject:
            if tail_subject.aggregation == "composite":
                self.draw_head = draw_head_composite
            elif tail_subject.aggregation == "shared":
                self.draw_head = draw_head_shared
            elif head_subject.navigability is True:
                self.draw_head = draw_head_navigable
            elif head_subject.navigability is False:
                self.draw_head = draw_head_none
            else:
                self.draw_head = draw_default_head

            if head_subject.aggregation == "composite":
                self.draw_tail = draw_tail_composite
            elif head_subject.aggregation == "shared":
                self.draw_tail = draw_tail_shared
            elif tail_subject.navigability is True:
                self.draw_tail = draw_tail_navigable
            elif tail_subject.navigability is False:
                self.draw_tail = draw_tail_none
            else:
                self.draw_tail = draw_default_tail
        else:
            if self.preferred_aggregation == "composite":
                self.draw_head = draw_head_composite
            elif self.preferred_aggregation == "shared":
                self.draw_head = draw_head_shared
            else:
                self.draw_head = draw_default_head
            self.draw_tail = draw_default_tail
        self.request_update()

    def update(self, _context: UpdateContext | None = None):
        self._head_end.update_text()
        self._tail_end.update_text()

    def point(self, x, y):
        """Returns the distance from the Association to the (mouse) cursor."""
        return min(
            super().point(x, y), self._head_end.point(x, y), self._tail_end.point(x, y)
        )

    def draw(self, context):
        super().draw(context)

        if self.subject and self.subject.abstraction:  # type: ignore[attr-defined]
            draw_information_flow(
                self,
                context,
                self.subject.memberEnd[0]
                in self.subject.abstraction[:].informationTarget,  # type: ignore[attr-defined]
            )

        if self.show_direction:
            pos, angle = get_center_pos(self.handles())
            inv = (
                -1
                if (
                    self.tail_subject and self.tail_subject is self.subject.memberEnd[0]
                )
                else 1
            )
            with cairo_state(context.cairo) as cr:
                cr.translate(*pos)
                if -half_pi <= angle < half_pi:
                    angle += pi
                    inv *= -1
                cr.rotate(angle)
                cr.move_to(0, 2)
                cr.line_to(6 * inv, 7)
                cr.line_to(0, 12)
                cr.fill()


def draw_head_none(context):
    """Draw an 'x' on the line end to indicate no navigability at association
    head."""
    cr = context.cairo
    cr.move_to(6, -4)
    cr.rel_line_to(8, 8)
    cr.rel_move_to(0, -8)
    cr.rel_line_to(-8, 8)
    cr.move_to(0, 0)


def draw_tail_none(context):
    """Draw an 'x' on the line end to indicate no navigability at association
    tail."""
    cr = context.cairo
    cr.line_to(0, 0)
    cr.move_to(6, -4)
    cr.rel_line_to(8, 8)
    cr.rel_move_to(0, -8)
    cr.rel_line_to(-8, 8)


def _draw_diamond(cr):
    """Helper function to draw diamond shape for shared and composite
    aggregations."""
    cr.move_to(20, 0)
    cr.line_to(10, -6)
    cr.line_to(0, 0)
    cr.line_to(10, 6)
    cr.close_path()


def draw_head_composite(context):
    """Draw a closed diamond on the line end to indicate composite aggregation
    at association head."""
    cr = context.cairo
    _draw_diamond(cr)
    context.cairo.fill_preserve()
    cr.move_to(20, 0)


def draw_tail_composite(context):
    """Draw a closed diamond on the line end to indicate composite aggregation
    at association tail."""
    cr = context.cairo
    cr.line_to(20, 0)
    stroke(context, fill=True)
    _draw_diamond(cr)
    cr.fill_preserve()
    stroke(context, fill=True)


def draw_head_shared(context):
    """Draw an open diamond on the line end to indicate shared aggregation at
    association head."""
    cr = context.cairo
    _draw_diamond(cr)
    cr.move_to(20, 0)


def draw_tail_shared(context):
    """Draw an open diamond on the line end to indicate shared aggregation at
    association tail."""
    cr = context.cairo
    cr.line_to(20, 0)
    _draw_diamond(cr)


def draw_head_navigable(context):
    """Draw a normal arrow to indicate association end navigability at
    association head."""
    cr = context.cairo
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    cr.move_to(0, 0)


def draw_tail_navigable(context):
    """Draw a normal arrow to indicate association end navigability at
    association tail."""
    cr = context.cairo
    cr.line_to(0, 0)
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)


class AssociationEnd:
    """An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and one
    for the multiplicity (and maybe one for tagged values in the future).

    An AsociationEnd has no ID, hence it will not be stored, but it will
    be recreated by the owning Association.
    """

    def __init__(self, owner: AssociationItem, end: Optional[str] = None):
        self._canvas = None
        self._owner = owner
        self._end = end

        # Rendered text for name and multiplicity
        self._name = ""
        self._mult = ""

        self._name_bounds = Rectangle()
        self._mult_bounds = Rectangle()

        self._name_shape = Text(text=lambda: self._name)
        self._mult_shape = Text(text=lambda: self._mult)

    @property
    def name_bounds(self):
        return self._name_bounds

    @property
    def owner(self) -> AssociationItem:
        """Override Element.owner."""
        return self._owner

    @property
    def owner_handle(self) -> Handle:
        # handle(event) is the event handler method
        return self._owner.head if self is self._owner.head_end else self._owner.tail

    @property
    def subject(self) -> Optional[UML.Property]:
        return getattr(self.owner, f"{self._end}_subject")  # type:ignore[no-any-return]

    @property
    def name(self):
        return self._name

    def update_text(self):
        """Set the text on the association end."""
        if self.subject:
            try:
                n, m = format_association_end(self.subject)
            except ValueError:
                # need more than 0 values to unpack: property was rendered as
                # attribute while in a UNDO action for example.
                pass
            else:
                self._name = n
                self._mult = m

    def update_position(self, context: UpdateContext, p1, p2):
        """Update label placement for association's name and multiplicity
        label.

        p1 is the line end and p2 is the last but one point of the line.
        """
        padding_top, padding_right, padding_bottom, padding_left = context.style.get(
            "padding", DEFAULT_PADDING
        )

        dx = float(p2[0]) - float(p1[0])
        dy = float(p2[1]) - float(p1[1])

        child_context = replace(
            context,
            style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
        )

        name_w, name_h = self._name_shape.size(child_context)
        mult_w, mult_h = self._mult_shape.size(child_context)

        rc = 1000.0 if dy == 0 else dx / dy
        abs_rc = abs(rc)
        left_side = dx > 0
        top_side = dy > 0

        if abs_rc > 6:
            # horizontal line
            name_dy = -padding_top - padding_bottom - name_h
            mult_dy = padding_top + padding_bottom
            if left_side:
                name_dx = padding_left
                mult_dx = padding_left
            else:
                name_dx = -padding_right - name_w
                mult_dx = -padding_right - mult_w
        elif 0 <= abs_rc <= 0.2:
            # vertical line
            line_width = context.style.get("line-width", 2)
            name_dx = -padding_left - padding_right - name_w - line_width
            mult_dx = padding_left + padding_right + line_width
            if top_side:
                name_dy = padding_top
                mult_dy = padding_top
            else:
                name_dy = -padding_bottom - name_h
                mult_dy = -padding_bottom - mult_h
        else:
            # Should both items be placed on the same side of the line?
            same_side = abs_rc < 1.0

            # Find out alignment of text (depends on the direction of the line)
            align_left = left_side ^ same_side
            align_top = top_side ^ same_side
            if align_left:
                name_dx = padding_left
                mult_dx = padding_left
            else:
                name_dx = -padding_right - name_w
                mult_dx = -padding_right - mult_w
            if align_top:
                name_dy = -padding_bottom - name_h
                mult_dy = -padding_bottom - name_h - mult_h
            else:
                name_dy = padding_top
                mult_dy = padding_top + mult_h

        self._name_bounds = Rectangle(
            p1[0] + name_dx, p1[1] + name_dy, width=name_w, height=name_h
        )

        self._mult_bounds = Rectangle(
            p1[0] + mult_dx, p1[1] + mult_dy, width=mult_w, height=mult_h
        )

    def point(self, x, y):
        """Given a point (x, y) return the distance to the diagram item."""
        drp = distance_rectangle_point
        pos = (x, y)
        d1 = drp(self._name_bounds, pos)
        d2 = drp(self._mult_bounds, pos)
        d3 = 1000.0
        return min(d1, d2, d3)

    def size(
        self, context: UpdateContext, bounding_box: Rectangle | None = None
    ) -> tuple[Number, Number]:
        handles = self.owner.handles()

        if self._end == "head":
            self.update_position(context, handles[0].pos, handles[1].pos)
        elif self._end == "tail":
            self.update_position(context, handles[-1].pos, handles[-2].pos)

        bounds = self._name_bounds + self._mult_bounds
        return bounds.width, bounds.height

    def draw(self, context: DrawContext, _bounding_box: Rectangle) -> None:
        """Draw name and multiplicity of the line end."""
        if not self.subject:
            return

        # Padding has been taken into account when calculating name and mult bounds
        child_context = replace(
            context,
            style={k: v for k, v in context.style.items() if k != "padding"},  # type: ignore[arg-type]
        )

        self._name_shape.draw(child_context, self._name_bounds)
        self._mult_shape.draw(child_context, self._mult_bounds)

    def __iter__(self):
        yield self._name_shape
        yield self._mult_shape
