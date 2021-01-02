"""
Association item - graphical representation of an association.

Plan:
 - transform AssociationEnd in a (dumb) data class
 - for association name and direction tag, use the same trick as is used
   for line ends.
"""

# TODO: for Association.postload(): in some cases where the association ends
#   are connected to the same Class, the head_end property is connected to the
#   tail end and visa versa.


from math import atan2, pi

from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor import UML
from gaphor.core.modeling.presentation import Presentation, Transient
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import Style
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import (
    Box,
    EditableText,
    Text,
    cairo_state,
    combined_style,
    draw_default_head,
    draw_default_tail,
    text_draw_focus_box,
)
from gaphor.diagram.support import represents
from gaphor.diagram.text import Layout, middle_segment
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.UML.umlfmt import format_association_end


@represents(UML.Association)
class AssociationItem(LinePresentation[UML.Association], Named):
    """AssociationItem represents associations.

    An AssociationItem has two AssociationEnd items. Each AssociationEnd
    item represents a Property (with Property.association == my
    association).
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        # AssociationEnds are really inseparable from the AssociationItem.
        # We give them the same id as the association item.
        self._head_end = AssociationEnd(owner=self, end="head")
        self._tail_end = AssociationEnd(owner=self, end="tail")

        # Direction depends on the ends that hold the ownedEnd attributes.
        self._dir_angle = 0
        self._dir_pos = 0, 0

        self.shape_middle = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            EditableText(text=lambda: self.subject.name or ""),
        )

        # For the association ends:
        base = "subject[Association].memberEnd[Property]"
        self.watch("subject[NamedElement].name").watch(
            "subject.appliedStereotype.classifier.name"
        ).watch(f"{base}.name", self.on_association_end_value).watch(
            f"{base}.aggregation", self.on_association_end_value
        ).watch(
            f"{base}.appliedStereotype.slot.definingFeature.name",
            self.on_association_end_value,
        ).watch(
            f"{base}.appliedStereotype.slot.value", self.on_association_end_value
        ).watch(
            f"{base}.classifier", self.on_association_end_value
        ).watch(
            f"{base}.visibility", self.on_association_end_value
        ).watch(
            f"{base}.lowerValue", self.on_association_end_value
        ).watch(
            f"{base}.upperValue", self.on_association_end_value
        ).watch(
            f"{base}.owningAssociation", self.on_association_end_value
        ).watch(
            f"{base}.type[Class].ownedAttribute", self.on_association_end_value
        ).watch(
            f"{base}.type[Interface].ownedAttribute", self.on_association_end_value
        ).watch(
            f"{base}.appliedStereotype.classifier", self.on_association_end_value
        ).watch(
            "subject[Association].memberEnd"
        ).watch(
            "subject[Association].ownedEnd"
        ).watch(
            "subject[Association].navigableOwnedEnd"
        ).watch(
            "show_direction"
        )

    show_direction: attribute[bool] = attribute("show_direction", bool, False)

    def save(self, save_func):
        super().save(save_func)
        if self._head_end.subject:
            save_func("head-subject", self._head_end.subject)
        if self._tail_end.subject:
            save_func("tail-subject", self._tail_end.subject)

    def load(self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ("head_end", "head_subject", "head-subject"):
            self._head_end.subject = value
        elif name in ("tail_end", "tail_subject", "tail-subject"):
            self._tail_end.subject = value
        else:
            super().load(name, value)

    def postload(self):
        super().postload()
        self._head_end.set_text()
        self._tail_end.set_text()

    head_end = property(lambda self: self._head_end)

    tail_end = property(lambda self: self._tail_end)

    def unlink(self):
        self._head_end.unlink()
        self._tail_end.unlink()
        super().unlink()

    def invert_direction(self):
        """Invert the direction of the association, this is done by swapping
        the head and tail-ends subjects."""
        if not self.subject:
            return

        self.subject.memberEnd.swap(
            self.subject.memberEnd[0], self.subject.memberEnd[1]
        )
        self.request_update()

    def on_association_end_value(self, event):
        """Handle events and update text on association end."""
        for end in (self._head_end, self._tail_end):
            end.set_text()
        self.request_update()

    def post_update(self, context):
        """Update the shapes and sub-items of the association."""

        handles = self.handles()

        # Update line endings:
        head_subject = self._head_end.subject
        tail_subject = self._tail_end.subject

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
            if self.show_direction:
                inverted = self.tail_end.subject is self.subject.memberEnd[0]
                pos, angle = get_center_pos(self.handles(), inverted)
                self._dir_pos = pos
                self._dir_angle = angle
        else:
            self.draw_head = draw_default_head
            self.draw_tail = draw_default_tail

        # update relationship after self.set calls to avoid circural updates
        super().post_update(context)

        # Calculate alignment of the head name and multiplicity
        self._head_end.post_update(context, handles[0].pos, handles[1].pos)

        # Calculate alignment of the tail name and multiplicity
        self._tail_end.post_update(context, handles[-1].pos, handles[-2].pos)

    def point(self, x, y):
        """Returns the distance from the Association to the (mouse) cursor."""
        return min(
            super().point(x, y), self._head_end.point(x, y), self._tail_end.point(x, y)
        )

    def draw(self, context):
        super().draw(context)
        self._head_end.draw(context)
        self._tail_end.draw(context)
        if self.show_direction:
            with cairo_state(context.cairo) as cr:
                cr.translate(*self._dir_pos)
                cr.rotate(self._dir_angle)
                cr.move_to(0, 0)
                cr.line_to(6, 5)
                cr.line_to(0, 10)
                cr.fill()


def get_center_pos(points, inverted=False):
    """Return position in the centre of middle segment of a line.

    Angle of the middle segment is also returned.
    """
    h0, h1 = middle_segment(points)
    pos = (h0.pos.x + h1.pos.x) / 2, (h0.pos.y + h1.pos.y) / 2
    angle = atan2(h1.pos.y - h0.pos.y, h1.pos.x - h0.pos.x)
    if inverted:
        angle += pi
    return pos, angle


def draw_head_none(context):
    """Draw an 'x' on the line end to indicate no navigability at association
    head."""
    cr = context.cairo
    cr.move_to(6, -4)
    cr.rel_line_to(8, 8)
    cr.rel_move_to(0, -8)
    cr.rel_line_to(-8, 8)
    cr.stroke()
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
    cr.stroke()


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
    cr.stroke()
    cr.move_to(20, 0)


def draw_tail_composite(context):
    """Draw a closed diamond on the line end to indicate composite aggregation
    at association tail."""
    cr = context.cairo
    cr.line_to(20, 0)
    cr.stroke()
    _draw_diamond(cr)
    cr.fill_preserve()
    cr.stroke()


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
    cr.stroke()
    _draw_diamond(cr)
    cr.stroke()


def draw_head_navigable(context):
    """Draw a normal arrow to indicate association end navigability at
    association head."""
    cr = context.cairo
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)
    cr.stroke()
    cr.move_to(0, 0)


def draw_tail_navigable(context):
    """Draw a normal arrow to indicate association end navigability at
    association tail."""
    cr = context.cairo
    cr.line_to(0, 0)
    cr.stroke()
    cr.move_to(15, -6)
    cr.line_to(0, 0)
    cr.line_to(15, 6)


class AssociationEnd(Presentation[UML.Property]):
    """An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and one
    for the multiplicity (and maybe one for tagged values in the future).

    An AsociationEnd has no ID, hence it will not be stored, but it will
    be recreated by the owning Association.
    """

    def __init__(self, owner, end=None):
        super().__init__(diagram=owner.diagram, id=Transient)
        self._canvas = None
        self._owner = owner
        self._end = end

        # Rendered text for name and multiplicity
        self._name = ""
        self._mult = ""

        self._name_bounds = Rectangle()
        self._mult_bounds = Rectangle()

        self._name_layout = Layout("")
        self._mult_layout = Layout("")

        self._inline_style: Style = {"font-size": 10}

    name_bounds = property(lambda s: s._name_bounds)

    @property
    def owner(self):
        """Override Element.owner."""
        return self._owner

    @property
    def owner_handle(self):
        # handle(event) is the event handler method
        return self._owner.head if self is self._owner.head_end else self._owner.tail

    def request_update(self):
        self._owner.request_update()

    def set_text(self):
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
                self.request_update()

    def get_name(self):
        return self._name

    def get_mult(self):
        return self._mult

    def post_update(self, context, p1, p2):
        """Update label placement for association's name and multiplicity
        label.

        p1 is the line end and p2 is the last but one point of the line.
        """
        style = combined_style(context.style, self._inline_style)
        ofs = 5

        dx = float(p2[0]) - float(p1[0])
        dy = float(p2[1]) - float(p1[1])

        def max_text_size(size1, size2):
            w1, h1 = size1
            w2, h2 = size2
            return (max(w1, w2), max(h1, h2))

        name_layout = self._name_layout
        name_layout.set_text(self._name)
        name_layout.set_font(style)
        name_w, name_h = max_text_size(name_layout.size(), (10, 10))

        mult_layout = self._mult_layout
        mult_layout.set_text(self._mult)
        mult_layout.set_font(style)
        mult_w, mult_h = max_text_size(mult_layout.size(), (10, 10))

        if dy == 0:
            rc = 1000.0  # quite a lot...
        else:
            rc = dx / dy
        abs_rc = abs(rc)
        h = dx > 0  # right side of the box
        v = dy > 0  # bottom side

        if abs_rc > 6:
            # horizontal line
            if h:
                name_dx = ofs
                name_dy = -ofs - name_h
                mult_dx = ofs
                mult_dy = ofs
            else:
                name_dx = -ofs - name_w
                name_dy = -ofs - name_h
                mult_dx = -ofs - mult_w
                mult_dy = ofs
        elif 0 <= abs_rc <= 0.2:
            # vertical line
            if v:
                name_dx = -ofs - name_w
                name_dy = ofs
                mult_dx = ofs
                mult_dy = ofs
            else:
                name_dx = -ofs - name_w
                name_dy = -ofs - name_h
                mult_dx = ofs
                mult_dy = -ofs - mult_h
        else:
            # Should both items be placed on the same side of the line?
            r = abs_rc < 1.0

            # Find out alignment of text (depends on the direction of the line)
            align_left = h ^ r
            align_bottom = v ^ r
            if align_left:
                name_dx = ofs
                mult_dx = ofs
            else:
                name_dx = -ofs - name_w
                mult_dx = -ofs - mult_w
            if align_bottom:
                name_dy = -ofs - name_h
                mult_dy = -ofs - name_h - mult_h
            else:
                name_dy = ofs
                mult_dy = ofs + mult_h

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

    def draw(self, context):
        """Draw name and multiplicity of the line end."""
        if not self.subject:
            return

        cr = context.cairo
        text_color = context.style.get("text-color")
        if text_color:
            cr.set_source_rgba(*text_color)

        cr.move_to(self._name_bounds.x, self._name_bounds.y)
        self._name_layout.show_layout(cr)
        cr.move_to(self._mult_bounds.x, self._mult_bounds.y)
        self._mult_layout.show_layout(cr)

        for b in (self._name_bounds, self._mult_bounds):
            text_draw_focus_box(context, b.x, b.y, b.width, b.height)
