"""
Association item - graphical representation of an association.

Plan:
 - transform AssociationEnd in a (dumb) data class
 - for assocation name and direction tag, use the same trick as is used
   for line ends.
"""

# TODO: for Association.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from gaphas.util import text_extents, text_align, text_multiline
from gaphas.state import reversible_property
from gaphas import Item
from gaphas.geometry import Rectangle, distance_point_point_fast
from gaphas.geometry import distance_rectangle_point, distance_line_point

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine


class AssociationItem(NamedLine):
    """
    AssociationItem represents associations. 
    An AssociationItem has two AssociationEnd items. Each AssociationEnd item
    represents a Property (with Property.association == my association).
    """

    __uml__ = UML.Association

    def __init__(self, id=None):
        NamedLine.__init__(self, id)

        # AssociationEnds are really inseperable from the AssociationItem.
        # We give them the same id as the association item.
        self._head_end = AssociationEnd(owner=self, end="head")
        self._tail_end = AssociationEnd(owner=self, end="tail")

        # Direction depends on the ends that hold the ownedEnd attributes.
        self._show_direction = False
        self._dir_angle = 0
        self._dir_pos = 0, 0
        
        #self.watch('subject<Association>.ownedEnd')\
            #.watch('subject<Association>.memberEnd')

        # For the association ends:
        base = 'subject<Association>.memberEnd<Property>.'
        self.watch(base + 'name', self.on_association_end_value)\
            .watch(base + 'aggregation', self.on_association_end_value)\
            .watch(base + 'classifier', self.on_association_end_value)\
            .watch(base + 'visibility', self.on_association_end_value)\
            .watch(base + 'lowerValue', self.on_association_end_value)\
            .watch(base + 'upperValue', self.on_association_end_value)\
            .watch(base + 'owningAssociation', self.on_association_end_value) \
            .watch(base + 'type<Class>.ownedAttribute', self.on_association_end_value) \
            .watch(base + 'type<Interface>.ownedAttribute', self.on_association_end_value) \
            .watch('subject<Association>.ownedEnd') \
            .watch('subject<Association>.navigableOwnedEnd')

    def set_show_direction(self, dir):
        self._show_direction = dir
        self.request_update()

    show_direction = reversible_property(lambda s: s._show_direction, set_show_direction)

    def setup_canvas(self):
        super(AssociationItem, self).setup_canvas()

    def teardown_canvas(self):
        super(AssociationItem, self).teardown_canvas()

    def save(self, save_func):
        NamedLine.save(self, save_func)
        save_func('show-direction', self._show_direction)
        if self._head_end.subject:
            save_func('head-subject', self._head_end.subject)
        if self._tail_end.subject:
            save_func('tail-subject', self._tail_end.subject)

    def load(self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ( 'head_end', 'head_subject', 'head-subject' ):
            #type(self._head_end).subject.load(self._head_end, value)
            #self._head_end.load('subject', value)
            self._head_end.subject = value
        elif name in ( 'tail_end', 'tail_subject', 'tail-subject' ):
            #type(self._tail_end).subject.load(self._tail_end, value)
            #self._tail_end.load('subject', value)
            self._tail_end.subject = value
        else:
            NamedLine.load(self, name, value)

    def postload(self):
        NamedLine.postload(self)
        self._head_end.set_text()
        self._tail_end.set_text()

    head_end = property(lambda self: self._head_end)

    tail_end = property(lambda self: self._tail_end)

    def unlink(self):
        self._head_end.unlink()
        self._tail_end.unlink()
        super(AssociationItem, self).unlink()

    def invert_direction(self):
        """
        Invert the direction of the association, this is done by swapping
        the head and tail-ends subjects.
        """
        if not self.subject:
            return

        self.subject.memberEnd.swap(self.subject.memberEnd[0], self.subject.memberEnd[1])
        self.request_update()

    def on_named_element_name(self, event):
        """
        Update names of the association as well as its ends.

        Override NamedLine.on_named_element_name.
        """
        if event is None:
            super(AssociationItem, self).on_named_element_name(event)
            self.on_association_end_value(event)
        elif event.element is self.subject:
            super(AssociationItem, self).on_named_element_name(event)
        else:
            self.on_association_end_value(event)

    def on_association_end_value(self, event):
        """
        Handle events and update text on association end.
        """
        #if event:
        #    element = event.element
        #    for end in (self._head_end, self._tail_end):
        #        subject = end.subject
        #        if subject and element in (subject, subject.lowerValue, \
        #                subject.upperValue, subject.taggedValue):
        #            end.set_text()
        #            self.request_update()
        ##            break;
        #else:
        for end in (self._head_end, self._tail_end):
            end.set_text()
        self.request_update()

            

    def post_update(self, context):
        """
        Update the shapes and sub-items of the association.
        """

        handles = self.handles()

        # Update line endings:
        head_subject = self._head_end.subject
        tail_subject = self._tail_end.subject
        
        # Update line ends using the aggregation and isNavigable values:
        if head_subject and tail_subject:
            if tail_subject.aggregation == intern('composite'):
                self.draw_head = self.draw_head_composite
            elif tail_subject.aggregation == intern('shared'):
                self.draw_head = self.draw_head_shared
            elif self._head_end.subject.navigability is True:
                self.draw_head = self.draw_head_navigable
            elif self._head_end.subject.navigability is False:
                self.draw_head = self.draw_head_none
            else:
                self.draw_head = self.draw_head_undefined

            if head_subject.aggregation == intern('composite'):
                self.draw_tail = self.draw_tail_composite
            elif head_subject.aggregation == intern('shared'):
                self.draw_tail = self.draw_tail_shared
            elif self._tail_end.subject.navigability is True:
                self.draw_tail = self.draw_tail_navigable
            elif self._tail_end.subject.navigability is False:
                self.draw_tail = self.draw_tail_none
            else:
                self.draw_tail = self.draw_tail_undefined

            if self._show_direction:
                inverted = self.tail_end.subject is self.subject.memberEnd[0]
                pos, angle = self._get_center_pos(inverted)
                self._dir_pos = pos
                self._dir_angle = angle
        else:
            self.draw_head = self.draw_head_undefined
            self.draw_tail = self.draw_tail_undefined

        # update relationship after self.set calls to avoid circural updates
        super(AssociationItem, self).post_update(context)

        # Calculate alignment of the head name and multiplicity
        self._head_end.post_update(context, handles[0].pos,
                                     handles[1].pos)

        # Calculate alignment of the tail name and multiplicity
        self._tail_end.post_update(context, handles[-1].pos,
                                     handles[-2].pos)
        

    def point(self, pos):
        """
        Returns the distance from the Association to the (mouse) cursor.
        """
        return min(super(AssociationItem, self).point(pos),
                   self._head_end.point(pos),
                   self._tail_end.point(pos))

    def draw_head_none(self, context):
        """
        Draw an 'x' on the line end to indicate no navigability at
        association head.
        """
        cr = context.cairo
        cr.move_to(6, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()
        cr.move_to(0, 0)


    def draw_tail_none(self, context):
        """
        Draw an 'x' on the line end to indicate no navigability at
        association tail.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.move_to(6, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()


    def _draw_diamond(self, cr):
        """
        Helper function to draw diamond shape for shared and composite
        aggregations.
        """
        cr.move_to(20, 0)
        cr.line_to(10, -6)
        cr.line_to(0, 0)
        cr.line_to(10, 6)
        #cr.line_to(20, 0)
        cr.close_path()


    def draw_head_composite(self, context):
        """
        Draw a closed diamond on the line end to indicate composite
        aggregation at association head.
        """
        cr = context.cairo
        self._draw_diamond(cr)
        context.cairo.fill_preserve()
        cr.stroke()
        cr.move_to(20, 0)


    def draw_tail_composite(self, context):
        """
        Draw a closed diamond on the line end to indicate composite
        aggregation at association tail.
        """
        cr = context.cairo
        cr.line_to(20, 0)
        cr.stroke()
        self._draw_diamond(cr)
        cr.fill_preserve()
        cr.stroke()


    def draw_head_shared(self, context):
        """
        Draw an open diamond on the line end to indicate shared aggregation
        at association head.
        """
        cr = context.cairo
        self._draw_diamond(cr)
        cr.move_to(20, 0)


    def draw_tail_shared(self, context):
        """
        Draw an open diamond on the line end to indicate shared aggregation
        at association tail.
        """
        cr = context.cairo
        cr.line_to(20, 0)
        cr.stroke()
        self._draw_diamond(cr)
        cr.stroke()


    def draw_head_navigable(self, context):
        """
        Draw a normal arrow to indicate association end navigability at
        association head.
        """
        cr = context.cairo
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.stroke()
        cr.move_to(0, 0)


    def draw_tail_navigable(self, context):
        """
        Draw a normal arrow to indicate association end navigability at
        association tail.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


    def draw_head_undefined(self, context):
        """
        Draw nothing to indicate undefined association end at association
        head.
        """
        context.cairo.move_to(0, 0)


    def draw_tail_undefined(self, context):
        """
        Draw nothing to indicate undefined association end at association
        tail.
        """
        context.cairo.line_to(0, 0)


    def draw(self, context):
        super(AssociationItem, self).draw(context)
        cr = context.cairo
        self._head_end.draw(context)
        self._tail_end.draw(context)
        if self._show_direction:
            cr.save()
            try:
                cr.translate(*self._dir_pos)
                cr.rotate(self._dir_angle)
                cr.move_to(0, 0)
                cr.line_to(6, 5)
                cr.line_to(0, 10)
                cr.fill()
            finally:
                cr.restore()


    def item_at(self, x, y):
        if distance_point_point_fast(self._handles[0].pos, (x, y)) < 10:
            return self._head_end
        elif distance_point_point_fast(self._handles[-1].pos, (x, y)) < 10:
            return self._tail_end
        return self
        
        
class AssociationEnd(UML.Presentation):
    """
    An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and
    one for the multiplicity (and maybe one for tagged values in the future).

    An AsociationEnd has no ID, hence it will not be stored, but it will be
    recreated by the owning Association.
    
    TODO:
    - add on_point() and let it return min(distance(_name), distance(_mult)) or
      the first 20-30 units of the line, for association end popup menu.
    """

    
    def __init__(self, owner, id=None, end=None):
        UML.Presentation.__init__(self, id=False) # Transient object
        self._owner = owner
        self._end = end
        
        # Rendered text for name and multiplicity
        self._name = None
        self._mult = None

        self._name_bounds = Rectangle()
        self._mult_bounds = Rectangle()


    def request_update(self):
        self._owner.request_update()


    def set_text(self):
        """
        Set the text on the association end.
        """
        if self.subject:
            try:
                n, m = UML.format(self.subject)
            except ValueError:
                # need more than 0 values to unpack: property was rendered as
                # attribute while in a UNDO action for example.
                pass
            else:
                self._name = n
                self._mult = m
                self.request_update()


    def point_name(self, pos):
        drp = distance_rectangle_point
        return drp(self._name_bounds, pos)


    def point_mult(self, pos):
        drp = distance_rectangle_point
        return drp(self._mult_bounds, pos)


    def point(self, pos):
        return min(self.point_name(pos), self.point_mult(pos))


    def get_name(self):
        return self._name


    def get_mult(self):
        return self._mult


    def post_update(self, context, p1, p2):
        """
        Update label placement for association's name and
        multiplicity label. p1 is the line end and p2 is the last
        but one point of the line.
        """
        cr = context.cairo
        ofs = 5

        name_dx = 0.0
        name_dy = 0.0
        mult_dx = 0.0
        mult_dy = 0.0

        dx = float(p2[0]) - float(p1[0])
        dy = float(p2[1]) - float(p1[1])
        
        name_w, name_h = map(max, text_extents(cr, self._name, multiline=True), (10, 10))
        mult_w, mult_h = map(max, text_extents(cr, self._mult, multiline=True), (10, 10))

        if dy == 0:
            rc = 1000.0 # quite a lot...
        else:
            rc = dx / dy
        abs_rc = abs(rc)
        h = dx > 0 # right side of the box
        v = dy > 0 # bottom side

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
            align_left = (h and not r) or (r and not h)
            align_bottom = (v and not r) or (r and not v)
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

        self._name_bounds = Rectangle(p1[0] + name_dx,
                                      p1[1] + name_dy,
                                      width=name_w,
                                      height=name_h)

        self._mult_bounds = Rectangle(p1[0] + mult_dx,
                                      p1[1] + mult_dy,
                                      width=mult_w,
                                      height=mult_h)


    def point(self, pos):
        """Given a point (x, y) return the distance to the canvas item.
        """
        drp = distance_rectangle_point
        d1 = drp(self._name_bounds, pos)
        d2 = drp(self._mult_bounds, pos)
#        try:
#            d3 = geometry.distance_point_point(self._point1, pos)
#            d4, dummy = distance_line_point(self._point1, self._point2, pos, 1.0, 0) #diacanvas.shape.CAP_ROUND)
#            if d3 < 15 and d4 < 5:
#                d3 = 0.0
#        except Exception, e:
#            log.error("Could not determine distance", exc_info=True)
        d3 = 1000.0
        return min(d1, d2, d3)


    def draw(self, context):
        """Draw name and multiplicity of the line end.
        """
        if not self.subject:
            return

        cr = context.cairo
        text_multiline(cr, self._name_bounds[0], self._name_bounds[1], self._name)
        text_multiline(cr, self._mult_bounds[0], self._mult_bounds[1], self._mult)
        cr.stroke()

        if context.hovered or context.focused or context.draw_all:
            cr.set_line_width(0.5)
            b = self._name_bounds
            cr.rectangle(b.x, b.y, b.width, b.height)
            cr.stroke()
            b = self._mult_bounds
            cr.rectangle(b.x, b.y, b.width, b.height)
            cr.stroke()
    

# vim:sw=4:et
