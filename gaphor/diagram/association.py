'''
AssociationItem -- Graphical representation of an association.
'''
# vim:sw=4:et

from __future__ import generators

import gobject
import diacanvas
import pango
import gaphor.UML as UML
from diagramitem import DiagramItem
from relationship import RelationshipItem

class AssociationItem(RelationshipItem, diacanvas.CanvasAbstractGroup):
    """AssociationItem represents associations. 
    An AssociationItem has two AssociationEnd items. Each AssociationEnd item
    represents a Property (with Property.association == my association).
    """
    
    def __init__(self, id=None):
        RelationshipItem.__init__(self, id)

        # AssociationEnds are really inseperable from the AssociationItem.
        # We give them the same id as the association item.
        self._head_end = AssociationEnd()
        self.add_construction(self._head_end)
        self._tail_end = AssociationEnd()
        self.add_construction(self._tail_end)

    def save (self, save_func):
        RelationshipItem.save(self, save_func)
        if self.head_end:
            save_func('head_end', self._head_end.subject)
        if self.tail_end:
            save_func('tail_end', self._tail_end.subject)

    def load (self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ( 'head_end', 'head-end' ):
            self._head_end.subject = value
        elif name in ( 'tail_end', 'tail-end' ):
            self._tail_end.subject = value
        else:
            RelationshipItem.load(self, name, value)

    def do_set_property (self, pspec, value):
        if pspec.name == 'head_end':
            self._head_end.subject = value
        elif pspec.name == 'tail_end':
            self._tail_end.subject = value
        else:
            RelationshipItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'head_end':
            return self._head_end.subject
        elif pspec.name == 'tail_end':
            return self._tail_end.subject
        else:
            return RelationshipItem.do_get_property(self, pspec)

    def has_capability(self, capability):
        if capability.startswith('head_'):
            subject = self._head_end.subject
        elif capability.startswith('tail_'):
            subject = self._tail_end.subject
        else:
            subject = None

        if subject:
            cap = capability[5:]
            if cap == 'is_navigable':
                # The side is navigable if the property is owned by the
                # class, if it is owned by the association, the side is
                # not navigable.
                return not subject.owningAssociation
            elif cap == 'ak_none':
                return (subject.aggregation == intern('none'))
            elif cap == 'ak_shared':
                return (subject.aggregation == intern('shared'))
            elif cap == 'ak_composite':
                return (subject.aggregation == intern('composite'))
        # in all other cases:
        return RelationshipItem.has_capability(self, capability)

    head_end = property(lambda self: self._head_end)

    tail_end = property(lambda self: self._tail_end)

    def on_subject_notify(self, pspec, notifiers=()):
        RelationshipItem.on_subject_notify(self, pspec,
                                           notifiers + ('ownedEnd',))

    def on_subject_notify__ownedEnd(self, subject, pspec):
        self.request_update()

    def on_update (self, affine):
        """Update the shapes and sub-items of the association."""
        # Update line endings:
        head_subject = self._head_end.subject
        tail_subject = self._tail_end.subject
        if head_subject and tail_subject:
            # Update line ends using the aggregation and isNavigable values:

            if head_subject.aggregation == intern('composite'):
                self.set(has_head=1, head_a=20, head_b=10, head_c=6, head_d=6,
                         head_fill_color=diacanvas.color(0,0,0,255))
            elif not head_subject.owningAssociation:
                # This side is navigable:
                self.set(has_head=1, head_a=0, head_b=15, head_c=6, head_d=6)
            else:
                self.set(has_head=0)

            if tail_subject.aggregation == intern('composite'):
                self.set(has_tail=1, tail_a=20, tail_b=10, tail_c=6, tail_d=6,
                         tail_fill_color=diacanvas.color(0,0,0,255))
            elif not tail_subject.owningAssociation:
                # This side is navigable:
                self.set(has_tail=1, tail_a=0, tail_b=15, tail_c=6, tail_d=6)
            else:
                self.set(has_tail=0)

        RelationshipItem.on_update(self, affine)

        handles = self.handles
        # Calculate alignment of the head name and multiplicity
        self._head_end.update_labels(handles[0].get_pos_i(),
                                     handles[1].get_pos_i())

        # Calculate alignment of the tail name and multiplicity
        self._tail_end.update_labels(handles[-1].get_pos_i(),
                                     handles[-2].get_pos_i())
        
        self.update_child(self._head_end, affine)
        self.update_child(self._tail_end, affine)

        # bounds calculation
        b1 = self.bounds
        b2 = self._head_end.get_bounds(self._head_end.affine)
        b3 = self._tail_end.get_bounds(self._tail_end.affine)
        self.set_bounds((min(b1[0], b2[0], b3[0]), min(b1[1], b2[1], b3[1]),
                         max(b1[2], b2[2], b3[2]), max(b1[3], b2[3], b3[3])))
                    
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        # Head and tail subjects are connected to an Association by 
        # Properties. Here we check if head_subject and tail_subject
        # already have an association. That association, however should not
        # be in our diagram yet.
        # 
        # Find all associations and determine if the properties on the
        # association ends have a type that points to the class.
        Association = UML.Association
        for assoc in GaphorResource(UML.ElementFactory).itervalues():
            if isinstance(assoc, Association):
                #print 'assoc.memberEnd', assoc.memberEnd
                end1 = assoc.memberEnd[0]
                end2 = assoc.memberEnd[1]
                if (end1.type is head_subject and end2.type is tail_subject) \
                   or (end2.type is head_subject and end1.type is tail_subject):
                    # check if this entry is not yet in the diagram
                    # Return if the association is not (yet) on the canvas
                    for item in assoc.presentation:
                        if item.canvas is self.canvas and item is not self:
                            break
                    else:
                        return end1, end2, assoc
        log.debug('No association found')
        return None, None, None
                    
    def allow_connect_handle(self, handle, connecting_to):
        """This method is called by a canvas item if the user tries to connect
        this object's handle. allow_connect_handle() checks if the line is
        allowed to be connected. In this case that means that one end of the
        line should be connected to a Comment.
        Returns: TRUE if connection is allowed, FALSE otherwise.
        """
        #log.debug('AssociationItem.allow_connect_handle')
        try:
            if not isinstance(connecting_to.subject, UML.Classifier):
                return 0

            # Also allow connections to the same class...
            c1 = self.handles[0].connected_to
            c2 = self.handles[-1].connected_to
            if not c1 and not c2:
                return 1
            if self.handles[0] is handle:
                return (self.handles[-1].connected_to.subject is not connecting_to.subject)
            elif self.handles[-1] is handle:
                return (self.handles[0].connected_to.subject is not connecting_to.subject)
            assert 1, 'Should never be reached...'
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """This method is called after a connection is established. This method
        sets the internal state of the line and updates the data model.
        """
        #log.debug('AssociationItem.confirm_connect_handle')
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            head_end, tail_end, relation = self.find_relationship(s1, s2)
            if not relation:
                element_factory = GaphorResource(UML.ElementFactory)
                relation = element_factory.create(UML.Association)
                head_end = element_factory.create(UML.Property)
                tail_end = element_factory.create(UML.Property)
                relation.package = self.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                head_end.type = head_end.clazz = s1
                tail_end.type = tail_end.clazz = s2

                # copy text from ends to AssociationEnds:
                head_end.name = self._head_end._name.get_property('text')
                #head_end.multiplicity = self._head__end._mult.get_property('text')
                tail_end.name = self._tail_end._name.get_property('text')
                #tail_end.multiplicity = self._tail_end._mult.get_property('text')
            self.subject = relation
            self._head_end.subject = head_end
            self._tail_end.subject = tail_end

    def confirm_disconnect_handle (self, handle, was_connected_to):
        log.debug('AssociationItem.confirm_disconnect_handle')
        if self.subject:
            del self.subject
            del self._head_end.subject
            del self._tail_end.subject

    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the name to be removed.'''
        #self.emit_stop_by_name('remove')
        ##return 0
        return 1

    def on_groupable_iter(self):
        return iter([self._head_end, self._tail_end])

    def on_groupable_length(self):
        return 2

    def on_groupable_pos(self, item):
        if item is self._head_end:
            return 0
        elif item is self._tail_end:
            return 1
        return -1


class AssociationEnd(diacanvas.CanvasItem, diacanvas.CanvasAbstractGroup, DiagramItem):
    """An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and
    one for the multiplicity (and maybe one for tagged values in the future).
    """
    __gproperties__ = DiagramItem.__gproperties__

    __gsignals__ = DiagramItem.__gsignals__

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        self.set_flags(diacanvas.COMPOSITE)
        self._name = AssociationLabel('name')
        self.add_construction(self._name)
        self._name.connect('notify::text', self.on_name_notify)
        self._mult = AssociationLabel('multiplicity')
        self.add_construction(self._mult)
        self._mult.connect('notify::text', self.on_mult_notify)

    # AssociationEnd's are inseperable from AssociationItem's. We even
    # pretend to have the same id (for loading and saving), since the
    # AssociationItem saves the subject.
    id = property(lambda self: self.parent.id, doc='Id')

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect

    def update_labels(self, p1, p2):
        """Update label placement for association's name and
        multiplicity label. p1 is the line end and p2 is the last
        but one point of the line."""
        ofs = 5

        name_dx = 0.0
        name_dy = 0.0
        mult_dx = 0.0
        mult_dy = 0.0

        dx = float(p2[0]) - float(p1[0])
        dy = float(p2[1]) - float(p1[1])
        
        name_label = self._name
        mult_label = self._mult

        if dy == 0:
            rc = 1000.0 # quite a lot...
        else:
            rc = dx / dy
        abs_rc = abs(rc)
        h = dx > 0 # right side of the box
        v = dy > 0 # bottom side

        layout = name_label.get_property('layout')
        name_w, name_h = layout.get_pixel_size()

        layout = mult_label.get_property('layout')
        mult_w, mult_h = layout.get_pixel_size()

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
        a = name_label.get_property('affine')
        name_label.set_property('affine', a[:4] + (p1[0] + name_dx, p1[1] + name_dy))
        name_label.set(width=name_w, height=name_h)
        a = mult_label.get_property('affine')
        mult_label.set_property('affine', a[:4] + (p1[0] + mult_dx, p1[1] + mult_dy))
        mult_label.set(width=mult_w, height=mult_h)

    def on_name_notify(self, label, pspec):
        assert label is self._name
        text = self._name.get_property('text')
        if self.subject.name != text:
            self.subject.name = text

    def on_mult_notify(self, label, pspec):
        assert label is self._mult
        text = self._mult.get_property('text')
        if not self.subject.lowerValue:
            self.subject.lowerValue = GaphorResource('ElementFactory').create(UML.LiteralSpecification)
        self.subject.lowerValue.value = text

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramItem.on_subject_notify(self, pspec,
                        notifiers + ('aggregation', 'name', 'lowerValue'))
        # Set name:
        if self.subject:
            if self.subject.name:
                self._name.set_property('text', self.subject.name)
            if self.subject.lowerValue:
                # Add a callback to lowerValue
                self._mult.set_property('text', self.subject.lowerValue.value)
        self.request_update()
        
    def on_subject_notify__aggregation(self, subject, pspec):
        self.request_update()

    def on_subject_notify__name(self, subject, pspec):
        if subject.name != self._name.get_property('text'):
            self._name.set_property('text', subject.name)

    def on_subject_notify__lowerValue(self, subject, pspec):
        print 'lowerValue', subject, subject.lowerValue
        if self.subject.lowerValue:
            self._mult.set_property('text', self.subject.lowerValue.value)
        # Add a callback to lowerValue

    def on_update(self, affine):
        diacanvas.CanvasItem.on_update(self, affine)
        self.update_child(self._name, affine)
        self.update_child(self._mult, affine)

        # bounds calculation
        b1 = self._name.get_bounds(self._name.affine)
        b2 = self._mult.get_bounds(self._mult.affine)
        self.set_bounds((min(b1[0], b2[0]), min(b1[1], b2[1]),
                         max(b1[2], b2[2]), max(b1[3], b2[3])))

    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the name to be removed.'''
        #self.emit_stop_by_name('remove')
        ##return 0
        return 1

    def on_groupable_iter(self):
        return iter([self._name, self._mult])

    def on_groupable_length(self):
        return 2

    def on_groupable_pos(self, item):
        if item is self._name:
            return 0
        elif item is self._mult:
            return 1
        return -1


class AssociationLabel(diacanvas.CanvasText):
    """This is a label that is placed on the end of an association.
    The label has a minimum width of 10 and shows a rectangle around then
    the association is selected.
    """
    LABEL_FONT='sans 10'

    def __init__(self, name):
        self.__gobject_init__()
        # don't call CanvasText.__init__(self), it will screw up the callbacks
        self.name = name
        font = pango.FontDescription(AssociationLabel.LABEL_FONT)
        self.set(font=font, multiline=False)
        self._border = diacanvas.shape.Path()
        self._border.set_color(diacanvas.color(128,128,128))
        self._border.set_line_width(1.0)
        #self.__border.set_visibility(diacanvas.shape.SHAPE_VISIBLE_IF_SELECTED)

    def on_update(self, affine):
        # Set a minimun width, so we can always select it
        w, h = self.get_property('layout').get_pixel_size()
        self.set_property('width', max(w, 10.0))

        diacanvas.CanvasText.on_update(self, affine)
        x1, y1, x2, y2 = self.get_bounds()
        self._border.rectangle((x1 + 0.5, y1 + 0.5), (x2 - 0.5, y2 - 0.5))

#    def on_event(self, event):
#        if event.type == diacanvas.EVENT_BUTTON_PRESS:
#            log.info('Edit Association ends %s' % self.name)
#        return diacanvas.CanvasText.on_event(self, event)

    def on_shape_iter(self):
        for i in diacanvas.CanvasText.on_shape_iter(self):
            yield i
        #if self.is_selected():
        yield self._border


gobject.type_register(AssociationItem)
diacanvas.set_groupable(AssociationItem)
gobject.type_register(AssociationEnd)
diacanvas.set_callbacks(AssociationEnd)
diacanvas.set_groupable(AssociationEnd)
gobject.type_register(AssociationLabel)
diacanvas.set_callbacks(AssociationLabel)

