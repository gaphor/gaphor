
"""AssociationItem -- Graphical representation of an association.

Plan:
 - transform AssociationEnd in a (dumb) data class
 - for assocation name and direction tag, use the same trick as is used
   for line ends.
 - 

"""

# TODO: for Association.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from math import atan, pi, sin, cos

from gaphas.util import text_extents
from gaphas import Item
from gaphas.geometry import Rectangle
from gaphas.geometry import distance_rectangle_point, distance_line_point

from gaphor import resource, UML
from gaphor.undomanager import undoable
#from gaphor.diagram import Relationship
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.diagramline import DiagramLine

#class AssociationRelationship(Relationship):
#    """Relationship for associations.
#    """
def xxx():
    def relationship(self, line, head_subject = None, tail_subject = None):
        # First check if we do not already contain the right subject:
        if line.subject:
            end1 = line.subject.memberEnd[0]
            end2 = line.subject.memberEnd[1]
            if (end1.type is head_type and end2.type is tail_type) \
               or (end2.type is head_type and end1.type is tail_type):
                return
                
        # Find all associations and determine if the properties on the
        # association ends have a type that points to the class.
        Association = UML.Association
        for assoc in resource(UML.ElementFactory).itervalues():
            if isinstance(assoc, Association):
                #print 'assoc.memberEnd', assoc.memberEnd
                end1 = assoc.memberEnd[0]
                end2 = assoc.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    # check if this entry is not yet in the diagram
                    # Return if the association is not (yet) on the canvas
                    for item in assoc.presentation:
                        if item.canvas is line.canvas:
                            break
                    else:
                        return assoc
        return None



class AssociationItem(DiagramLine):
    """AssociationItem represents associations. 
    An AssociationItem has two AssociationEnd items. Each AssociationEnd item
    represents a Property (with Property.association == my association).
    """

    __uml__ = UML.Association

    association_popup_menu = (
        'separator',
        'AssociationShowDirection',
        'AssociationInvertDirection',
        'separator',
#        'Side _A', (
#            'Head_isNavigable',
#            'separator',
#            'Head_AggregationNone',
#            'Head_AggregationShared',
#            'Head_AggregationComposite'),
#        'Side _B', (
#            'Tail_isNavigable',
#            'separator',
#            'Tail_AggregationNone',
#            'Tail_AggregationShared',
#            'Tail_AggregationComposite')
    )

    def __init__(self, id=None):
        DiagramLine.__init__(self, id)

        # AssociationEnds are really inseperable from the AssociationItem.
        # We give them the same id as the association item.
        self._label_pos = (0, 0)
        self._head_end = AssociationEnd(owner=self, end="head")
#        self._head_end.set_child_of(self)
        self._tail_end = AssociationEnd(owner=self, end="tail")
#        self._tail_end.set_child_of(self)

#        self._label = diacanvas.shape.Text()
#        self._label.set_font_description(pango.FontDescription(AssociationItem.FONT))
        #self._label.set_alignment(pango.ALIGN_CENTER)
#        self._label.set_markup(False)
        #self._label.set_max_width(100)
        #self._label.set_max_height(100)

        # Direction depends on the ends that hold the ownedEnd attributes.
        self._show_direction = False
#        self._dir = diacanvas.shape.Path()
#        self._dir.set_line_width(2.0)
#        self._dir.line(((10, 0), (10, 10), (0, 5)))
#        self._dir.set_fill_color(diacanvas.color(0,0,0))
#        self._dir.set_fill(diacanvas.shape.FILL_SOLID)
#        self._dir.set_cyclic(True)

#        self._head_xa = diacanvas.shape.Path()
#        self._head_xa.set_line_width(2.0)

#        self._head_xb = diacanvas.shape.Path()
#        self._head_xb.set_line_width(2.0)

#        self._tail_xa = diacanvas.shape.Path()
#        self._tail_xa.set_line_width(2.0)

#        self._tail_xb = diacanvas.shape.Path()
#        self._tail_xb.set_line_width(2.0)

    def setup_canvas(self):
        super(AssociationItem, self).setup_canvas()
        self._head_end._canvas = self.canvas
        self._tail_end._canvas = self.canvas

    def teardown_canvas(self):
        super(AssociationItem, self).teardown_canvas()
        del self._head_end._canvas
        del self._tail_end._canvas

    def save(self, save_func):
        DiagramLine.save(self, save_func)
        self.save_property(save_func, 'show-direction')
        if self._head_end.subject:
            save_func('head-subject', self._head_end.subject)
        if self._tail_end.subject:
            save_func('tail-subject', self._tail_end.subject)

    def load(self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ( 'head_end', 'head_subject', 'head-subject' ):
            #type(self._head_end).subject.load(self._head_end, value)
            self._head_end.load('subject', value)
        elif name in ( 'tail_end', 'tail_subject', 'tail-subject' ):
            #type(self._tail_end).subject.load(self._tail_end, value)
            self._tail_end.load('subject', value)
        else:
            DiagramLine.load(self, name, value)

    def postload(self):
        DiagramLine.postload(self)
        self._head_end.postload()
        self._tail_end.postload()

#    def do_set_property(self, pspec, value):
#        if pspec.name == 'head-subject':
#            self._head_end.subject = value
#        elif pspec.name == 'tail-subject':
#            self._tail_end.subject = value
#        elif pspec.name == 'show-direction':
#            self.preserve_property('show-direction')
#            self._show_direction = value
#            self.request_update()
#        else:
#            DiagramLine.do_set_property(self, pspec, value)

#    def do_get_property(self, pspec):
#        if pspec.name == 'head':
#            return self._head_end
#        if pspec.name == 'tail':
#            return self._tail_end
#        elif pspec.name == 'head-subject':
#            return self._head_end.subject
#        elif pspec.name == 'tail-subject':
#            return self._tail_end.subject
#        elif pspec.name == 'show-direction':
#            return self._show_direction
#        else:
#            return DiagramLine.do_get_property(self, pspec)

    head_end = property(lambda self: self._head_end)

    tail_end = property(lambda self: self._tail_end)

    def unlink(self):
        self._head_end.unlink()
        self._tail_end.unlink()
        DiagramLine.unlink(self)

    def get_popup_menu(self):
        if self.subject:
            return self.popup_menu + self.association_popup_menu
        else:
            return self.popup_menu

    def invert_direction(self):
        """Invert the direction of the association, this is done by
        swapping the head and tail-ends subjects.
        """
        if not self.subject:
            return

        self.subject.memberEnd.moveDown(self.subject.memberEnd[0])

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramLine.on_subject_notify(self, pspec,
                                           notifiers + ('name', 'ownedEnd', 'memberEnd'))

        self.on_subject_notify__name(self.subject, pspec)

    def on_subject_notify__name(self, subject, pspec):
        #log.debug('Association name = %s' % (subject and subject.name))
        #if subject:
        #    self._label.set_text(subject.name or '')
        #else:
        #    self._label.set_text('')
        self.request_update()

    def on_subject_notify__ownedEnd(self, subject, pspec):
        self.request_update()

    def on_subject_notify__memberEnd(self, subject, pspec):
        self.request_update()

    def update_label(self, context, p1, p2):
        """Update the name label near the middle of the association.
        """
        cr = context.cairo
        w, h = text_extents(cr, self.subject and self.subject.name)

        x = p1[0] > p2[0] and w + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and h or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        self._label_pos = (x, y)
        #log.debug('label pos = (%d, %d)' % (x, y))
        #return x, y, max(x + 10, x + w), max(y + 10, y + h)
        return x, y, x + w, y + h


    def update_dir(self, p1, p2):
        """Create a small arrow near the middle of the association line and
        let it point in the direction of self.subject.memberEnd[0].
        Keep in mind that self.subject.memberEnd[0].class_ points to the class
        *not* pointed to by the arrow.
        """
        x = p1[0] < p2[0] and -8 or 8
        y = p1[1] >= p2[1] and -8 or 8
        x = (p1[0] + p2[0]) / 2.0 + x
        y = (p1[1] + p2[1]) / 2.0 + y
        
        try:
            angle = atan((p1[1] - p2[1]) / (p1[0] - p2[0])) #/ pi * 180.0
        except ZeroDivisionError:
            angle = pi * 1.5

        # Invert angle if member ends are inverted
        if self.subject.memberEnd[0] is self._tail_end.subject:
            angle += pi

        if p1[0] < p2[0]:
            angle += pi
        elif p1[0] == p2[0] and p1[1] > p2[1]:
            angle += pi
        #log.debug('rotation angle is %s' % (angle/pi * 180.0))

        sin_angle = sin(angle)
        cos_angle = cos(angle)

        def r(a, b):
            return (cos_angle * a - sin_angle * b + x, \
                    sin_angle * a + cos_angle * b + y)

        # Create an arrow around (0, 0), so it can be easely rotated:
        self._dir.line((r(-6, 0), r(6, -5), r(6, 5)))
        self._dir.set_cyclic(True)

        return x, y, x + 12, y + 10

    def update(self, context):
        """Update the shapes and sub-items of the association."""

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
            elif self._head_end.get_navigability():
                self.draw_head = self.draw_head_navigable
            if self._head_end.get_navigability() == False:
                self.draw_head = self.draw_head_none
            else:
                self.draw_head = self.draw_head_undefined

            if head_subject.aggregation == intern('composite'):
                self.draw_tail = self.draw_tail_composite
            elif head_subject.aggregation == intern('shared'):
                self.draw_tail = self.draw_tail_shared
            elif self._tail_end.get_navigability():
                # This side is navigable:
                self.draw_tail = draw_tail_navigable
            elif self._tail_end.get_navigability() == False:
                self.draw_tail = draw_tail_none
            else:
                self.draw_tail = self.draw_tail_undefined

        # update relationship after self.set calls to avoid circural updates
        DiagramLine.update(self, context)

        # Calculate alignment of the head name and multiplicity
        self._head_end.update(context, handles[0].pos,
                                     handles[1].pos)

        # Calculate alignment of the tail name and multiplicity
        self._tail_end.update(context, handles[-1].pos,
                                     handles[-2].pos)
        
        #self.update_child(self._head_end, affine)
        #self.update_child(self._tail_end, affine)

        # update name label:
        middle = len(handles)/2
        self._label_bounds = self.update_label(context, handles[middle-1].pos,
                                               handles[middle].pos)

#        if self._show_direction and self.subject and self.subject.memberEnd:
#            b0 = self.update_dir(handles[middle-1].pos,
#                                 handles[middle].pos)
#        else:
#            b0 = self.bounds

        # bounds calculation
#        b1 = self.bounds
#        b2 = self._head_end.get_bounds(self._head_end.affine)
#        b3 = self._tail_end.get_bounds(self._tail_end.affine)
#        bv = zip(self._label_bounds, b0, b1, b2, b3)
#        self.set_bounds((min(bv[0]), min(bv[1]), max(bv[2]), max(bv[3])))
                    
#    def on_shape_iter(self):
#        for s in DiagramLine.on_shape_iter(self):
#            yield s
#        yield self._label
#        if self._show_direction:
#            yield self._dir
#
#        if self._head_end.subject and self._tail_end.subject:
#            if self._tail_end.subject.aggregation == intern('none') \
#                    and self._head_end.get_navigability() == False:
#                yield self._head_xa
#                yield self._head_xb
#
#            if self._head_end.subject.aggregation == intern('none') \
#                    and self._tail_end.get_navigability() == False:
#                yield self._tail_xa
#                yield self._tail_xb

    def point(self, x, y):
        """Returns the distance from the Association to the (mouse) cursor.
        """
        return min(super(AssociationItem, self).point(x, y),
                   self._head_end.point(x, y),
                   self._tail_end.point(x, y))

    def draw_head_none(self, context):
        """Draw an 'x' on the line end, indicating no traversing.
        """
        cr = context.cairo
        cr.move_to(6, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()
        cr.move_to(0, 0)

    def draw_tail_none(self, context):
        """Draw an 'x' on the line end, indicating no traversing.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.move_to(-14, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()

    def draw_head_composite(self, context):
        """Draw a closed diamond on the line end.
        """
        self.draw_head_shared(context)
        context.cairo.fill_preserve()

    def draw_tail_composite(self, context):
        """Draw a closed diamond on the line end.
        """
        self.draw_tail_shared(context)
        context.cairo.fill_preserve()
        cr.stroke()

    def draw_head_shared(self, context):
        """Draw an open diamond on the line end.
        """
        cr = context.cairo
        cr.move_to(20, 0)
        cr.line_to(10, -6)
        cr.line_to(0, 0)
        cr.line_to(10, 6)
        cr.line_to(20, 0)

    def draw_tail_shared(self, context):
        """Draw an open diamond on the line end.
        """
        cr = context.cairo
        cr.line_to(-20, 0)
        cr.stroke()
        cr.line_to(-10, -6)
        cr.line_to(0, 0)
        cr.line_to(-10, 6)
        cr.line_to(-20, 0)

    def draw_head_navigable(self, context):
        """Draw a normal arrow.
        """
        cr = context.cairo
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.stroke()
        cr.move_to(0, 0)

    def draw_tail_navigable(self, context):
        """Draw a normal arrow.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.move_to(-15, -6)
        cr.line_to(0, 0)
        cr.line_to(-15, 6)
        cr.stroke()

    def draw_head_undefined(self, context):
        """Draw nothing. undefined.
        """
        context.cairo.move_to(0, 0)

    def draw_tail_undefined(self, context):
        """Draw nothing. undefined.
        """
        context.cairo.line_to(0, 0)

    def draw(self, context):
        super(AssociationItem, self).draw(context)
        self._head_end.draw(context)
        self._tail_end.draw(context)
        # TODO: draw direction and association name


    #
    # Gaphor Connection Protocol
    #

    def allow_connect_handle(self, handle, connecting_to):
        """This method is called by a canvas item if the user tries to connect
        this object's handle. allow_connect_handle() checks if the line is
        allowed to be connected. In this case that means that one end of the
        line should be connected to a Classifier.
        Returns: TRUE if connection is allowed, FALSE otherwise.
        """
        #log.debug('AssociationItem.allow_connect_handle')
        if isinstance(connecting_to.subject, UML.Classifier):
            return True
        return False

    def confirm_connect_handle(self, handle):
        """This method is called after a connection is established. This method
        sets the internal state of the line and updates the data model.
        """
        #log.debug('AssociationItem.confirm_connect_handle')

        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            head_type = c1.subject
            tail_type = c2.subject

            # First check if we do not already contain the right subject:
            if self.subject:
                end1 = self.subject.memberEnd[0]
                end2 = self.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    return
                    
            # Find all associations and determine if the properties on the
            # association ends have a type that points to the class.
            Association = UML.Association
            for assoc in resource(UML.ElementFactory).itervalues():
                if isinstance(assoc, Association):
                    #print 'assoc.memberEnd', assoc.memberEnd
                    end1 = assoc.memberEnd[0]
                    end2 = assoc.memberEnd[1]
                    if (end1.type is head_type and end2.type is tail_type) \
                       or (end2.type is head_type and end1.type is tail_type):
                        # check if this entry is not yet in the diagram
                        # Return if the association is not (yet) on the canvas
                        for item in assoc.presentation:
                            if item.canvas is self.canvas:
                                break
                        else:
                            #return end1, end2, assoc
                            self.subject = assoc
                            if (end1.type is head_type and end2.type is tail_type):
                                self._head_end.subject = end1
                                self._tail_end.subject = end2
                            else:
                                self._head_end.subject = end2
                                self._tail_end.subject = end1
                            return
            else:
                # TODO: How should we handle other types than Class???

                element_factory = resource(UML.ElementFactory)
                relation = element_factory.create(UML.Association)
                head_end = element_factory.create(UML.Property)
                head_end.lowerValue = element_factory.create(UML.LiteralSpecification)
                tail_end = element_factory.create(UML.Property)
                tail_end.lowerValue = element_factory.create(UML.LiteralSpecification)
                relation.package = self.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                #head_end.type = tail_end.class_ = head_type
                #tail_end.type = head_end.class_ = tail_type
                head_end.type = head_type
                tail_end.type = tail_type
                head_type.ownedAttribute = tail_end
                tail_type.ownedAttribute = head_end
                # copy text from ends to AssociationEnds:
                #head_end.name = self._head_end._name.get_property('text')
                #head_end.multiplicity = self._head__end._mult.get_property('text')
                #tail_end.name = self._tail_end._name.get_property('text')
                #tail_end.multiplicity = self._tail_end._mult.get_property('text')

                self.subject = relation
                self._head_end.subject = head_end
                self._tail_end.subject = tail_end

    def confirm_disconnect_handle(self, handle, was_connected_to):
        #log.debug('AssociationItem.confirm_disconnect_handle')
        if self.subject:
            # First delete the Property's at the ends, otherwise they will
            # be interpreted as attributes.
            self._head_end.set_subject(None)
            self._tail_end.set_subject(None)
            self.set_subject(None)


class AssociationEnd(DiagramItem):
    """An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and
    one for the multiplicity (and maybe one for tagged values in the future).

    An AsociationEnd has no ID, hence it will not be stored, but it will be
    recreated by the owning Association.
    
    TODO:
    - add on_point() and let it return min(distance(_name), distance(_mult)) or
      the first 20-30 units of the line, for association end popup menu.
    """
#    __gproperties__ = {
#        'name': (gobject.TYPE_STRING, 'name', '', '', gobject.PARAM_READWRITE),
#        'mult': (gobject.TYPE_STRING, 'mult', '', '', gobject.PARAM_READWRITE)
#    }
#    __gproperties__.update(DiagramItem.__gproperties__)

    head_popup_menu = (
        'Head_unknownNavigation',
        'Head_isNotNavigable',
        'Head_isNavigable',
        'separator',
        'Head_AggregationNone',
        'Head_AggregationShared',
        'Head_AggregationComposite'
    )

    tail_popup_menu = (
        'Tail_unknownNavigation',
        'Tail_isNotNavigable',
        'Tail_isNavigable',
        'separator',
        'Tail_AggregationNone',
        'Tail_AggregationShared',
        'Tail_AggregationComposite'
    )

    def __init__(self, owner, id=None, end=None):
        DiagramItem.__init__(self, id)
        self._owner = owner
        self._end = end
        
        # Rendered text for name and multiplicity
        self._name = None
        self._mult = None

        self._name_bounds = Rectangle()
        self._mult_bounds = Rectangle()
        self._point1 = self._point2 = (0, 0)

    def postload(self):
        DiagramItem.postload(self)
        #self.set_text()

    def get_popup_menu(self):
        if self.subject:
            if self._end == 'head':
                return self.head_popup_menu
            else:
                return self.tail_popup_menu
        elif self.parent:
            return self.parent.get_popup_menu()

    def request_update(self):
        self._owner.request_update()

    def set_text(self):
        """Set the text on the association end.
        """
        if self.subject:
            try:
                n, m = self.subject.render()
            except ValueError:
                # need more than 0 values to unpack: property was rendered as
                # attribute while in a UNDO action for example.
                pass
            else:
                self._name = n
                self._mult = m
                self.request_update()


    def get_navigability(self):
        """
        Check navigability of the AssociationEnd. If property is owned by
        class via ownedAttribute, then it is navigable. If property is
        owned by association by owndedEnd, then it is not navigable.
        Otherwise the navigability is unknown.

        Returned navigability values:
            - None  - unknown
            - False - not navigable
            - True  - navigable
        """
        navigability = None # unknown navigability as default
        subject = self.subject

        if subject and subject.opposite:
            opposite = subject.opposite
            if isinstance(opposite.type, UML.Interface):
                type = subject.interface_
            else: # isinstance(opposite.type, UML.Class):
                type = subject.class_

            if type and subject in type.ownedAttribute:
                navigability = True
            elif subject.association and subject in subject.association.ownedEnd:
                navigability = False

        return navigability
                

    def set_navigable(self, navigable):
        """Change the AssociationEnd's navigability.

        A warning is issued if the subject or opposite property is missing.
        """
        subject = self.subject
        if subject and subject.opposite:
            opposite = subject.opposite

            #
            # Remove any navigability info, so unknown navigability state
            # is the default.
            #

            # if navigable
            if isinstance(opposite.type, UML.Class):
                if subject.class_:
                    del subject.class_
            elif isinstance(opposite.type, UML.Interface):
                if subject.interface_:
                    del subject.interface_
            else:
                assert 0, 'Should never be reached'

            # if not navigable
            if subject.owningAssociation:
                del subject.owningAssociation


            #
            # Set navigability.
            #
            if navigable:
                if isinstance(opposite.type, UML.Class):
                    subject.class_ = opposite.type
                elif isinstance(opposite.type, UML.Interface):
                    subject.interface_ = opposite.type
                else:
                    assert 0, 'Should never be reached'
            elif navigable == False:
                subject.owningAssociation = subject.association

            # else navigability is unknown

        else:
            log.warning('AssociationEnd.set_navigable: %s missing' % \
                        (subject and 'subject' or 'opposite Property'))


    def point_name(self, x, y):
        p = (x, y)
        drp = distance_rectangle_point
        return drp(self._name_bounds, p)

    def point_mult(self, x, y):
        p = (x, y)
        drp = distance_rectangle_point
        return drp(self._mult_bounds, p)

    def point(self, x, y):
        return min(self.point_name(x, y), self.point_mult(x, y))

    def edit_name(self):
        self.start_editing(self._name)

    def edit_mult(self):
        self.start_editing(self._mult)

    def update(self, context, p1, p2):
        """Update label placement for association's name and
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
        
        name_w, name_h = map(max, text_extents(cr, self._name), (10, 10))
        mult_w, mult_h = map(max, text_extents(cr, self._mult), (10, 10))

        if dy == 0:
            rc = 1000.0 # quite a lot...
        else:
            rc = dx / dy
        abs_rc = abs(rc)
        h = dx > 0 # right side of the box
        v = dy > 0 # bottom side

        if abs_rc > 6:
            #print 'horizontal line'
            if h:
                name_dx = ofs
                name_dy = -ofs - name_h # - height
                mult_dx = ofs
                mult_dy = ofs
            else:
                name_dx = -ofs - name_w
                name_dy = -ofs - name_h # - height
                mult_dx = -ofs - mult_w
                mult_dy = ofs
        elif 0 <= abs_rc <= 0.2:
            #print 'vertical line'
            if v:
                name_dx = -ofs - name_w # - width
                name_dy = ofs
                mult_dx = ofs
                mult_dy = ofs
            else:
                name_dx = -ofs - name_w # - width
                name_dy = -ofs - name_h # - height
                mult_dx = ofs
                mult_dy = -ofs - mult_h # - height
        else:
            r = abs_rc < 1.0
            align_left = (h and not r) or (r and not h)
            align_bottom = (v and not r) or (r and not v)
            if align_left:
                name_dx = ofs
                mult_dx = ofs
            else:
                name_dx = -ofs - name_w # - width
                mult_dx = -ofs - mult_w # - width
            if align_bottom:
                name_dy = -ofs - name_h # - height
                mult_dy = -ofs - name_h - mult_h # - height
            else:
                name_dy = ofs 
                mult_dy = ofs + mult_h # + height

        self._name_bounds = Rectangle(p1[0] + name_dx,
                                      p1[1] + name_dy,
                                      width=name_w,
                                      height=name_h)

        self._mult_bounds = Rectangle(p1[0] + mult_dx,
                                      p1[1] + mult_dy,
                                      width=mult_w,
                                      height=mult_h)

        self._point1 = p1
        self._point2 = p2

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramItem.on_subject_notify(self, pspec,
                        notifiers + ('aggregation', 'visibility',
                        'name', 'lowerValue.value',
                        'upperValue.value', 'taggedValue',
                        'owningAssociation', 'class_', 'interface_'))
        #print 'w/ assoc', self.subject and self.subject.association
        self.set_text()
        self.request_update()
        
    def on_subject_notify__aggregation(self, subject, pspec):
        self.request_update()

    def on_subject_notify__name(self, subject, pspec):
        self.set_text()

    def on_subject_notify__visibility(self, subject, pspec):
        self.set_text()

    def on_subject_notify__lowerValue_value(self, lower_value, pspec):
        log.debug('New value for lowerValue.value: %s' % lower_value and lower_value.value)
        self.set_text()
        self.request_update()

    def on_subject_notify__upperValue_value(self, upper_value, pspec):
        log.debug('New value for upperValue.value: %s' %  upper_value and upper_value.value)
        self.set_text()
        self.request_update()

    def on_subject_notify__taggedValue(self, tagged_value, pspec):
        self.set_text()
        self.request_update()

    def on_subject_notify__owningAssociation(self, upper_value, pspec):
        self.request_update()

    def on_subject_notify__class_(self, upper_value, pspec):
        self.request_update()

    def on_subject_notify__interface_(self, upper_value, pspec):
        self.request_update()

    def point(self, x, y):
        """Given a point (x, y) return the distance to the canvas item.
        """
        p = (x, y)
        drp = distance_rectangle_point
        d1 = drp(self._name_bounds, p)
        d2 = drp(self._mult_bounds, p)
#        try:
#            d3 = geometry.distance_point_point(self._point1, p)
#            d4, dummy = distance_line_point(self._point1, self._point2, p, 1.0, 0) #diacanvas.shape.CAP_ROUND)
#            if d3 < 15 and d4 < 5:
#                d3 = 0.0
#        except Exception, e:
#            log.error("Could not determine distance", e)
        d3 = 1000.0
        return min(d1, d2, d3)

    def draw(self, context):
        """Draw name and multiplicity of the line end.
        """
        if not self.subject:
            return

        cr = context.cairo
        cr.move_to(self._name_bounds[0], self._name_bounds[1])
        cr.show_text(self._name)
        cr.move_to(self._mult_bounds[0], self._mult_bounds[1])
        cr.show_text(self._mult)

        if context.hovered:
            cr.set_line_width(1.0)
            b = self._name_bounds
            cr.rectangle(b.x0, b.y0, b.width, b.height)
            cr.stroke()
            b = self._mult_bounds
            cr.rectangle(b.x0, b.y0, b.width, b.height)
            cr.stroke()
    

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        log.debug('association end edit on (%d,%d)' % (x, y))
        if self.point_name(x, y) < 1.0:
            return self._name 
        elif self.point_mult(x,y) < 1.0:
            return self._mult

    def on_editable_start_editing(self, shape):
        pass

    @undoable
    def on_editable_editing_done(self, shape, new_text):
        if shape in (self._name, self._mult):
            if self.subject and (shape == self._name or new_text != ''):
                self.subject.parse(new_text)
            #self.set_text()
            #log.info('editing done')


def rotate(p1, p2, points):
    """
    Rotate points around p1. Rotation angle is determined by line (p0, p1).
    Every point is moved into p1 + (10, 0) after rotation.
    """
    try:
        angle = atan((p1[1] - p2[1]) / (p1[0] - p2[0]))
    except ZeroDivisionError:
        angle = pi * 1.5
        

    sin_angle = sin(angle)
    cos_angle = cos(angle)

    def r(a, b, x, y):
        return (cos_angle * a - sin_angle * b + x,
                sin_angle * a + cos_angle * b + y)

    x0 = p1[0] < p2[0] and 10 or -10
    y0 = 0

    # rotate around the (10, 0)
    x0, y0 = r(x0, y0, 0, 0)

    # move to the destination point
    x0 += p1[0]
    y0 += p1[1]

    return [ r(x, y, x0, y0) for x, y in points ]


# vim:sw=4:et
