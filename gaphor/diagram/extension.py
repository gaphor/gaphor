'''
ExtensionItem -- Graphical representation of an association.
'''
# vim:sw=4:et

# TODO: for Extension.postload(): in some cases where the association ends
# are connected to the same Class, the head_end property is connected to the
# tail end and visa versa.

from __future__ import generators

import gobject
import pango
import diacanvas
import diacanvas.shape
import diacanvas.geometry
import gaphor
import gaphor.UML as UML
from gaphor.diagram import initialize_item

from diagramitem import DiagramItem
from relationship import RelationshipItem

class ExtensionItem(RelationshipItem, diacanvas.CanvasAbstractGroup):
    """ExtensionItem represents associations. 
    An ExtensionItem has two ExtensionEnd items. Each ExtensionEnd item
    represents a Property (with Property.association == my association).
    """
    __gproperties__ = {
        'head':         (gobject.TYPE_OBJECT, 'head',
                         'ExtensionEnd held by the head end of the association',
                         gobject.PARAM_READABLE),
        'tail':         (gobject.TYPE_OBJECT, 'tail',
                         'ExtensionEnd held by the tail end of the association',
                         gobject.PARAM_READABLE),
        'head-subject': (gobject.TYPE_PYOBJECT, 'head-subject',
                         'subject held by the head end of the association',
                         gobject.PARAM_READWRITE),
        'tail-subject': (gobject.TYPE_PYOBJECT, 'tail-subject',
                         'subject held by the tail end of the association',
                         gobject.PARAM_READWRITE),
    }

    def __init__(self, id=None):
        RelationshipItem.__init__(self, id)

        # ExtensionEnds are really inseperable from the ExtensionItem.
        # We give them the same id as the association item.
        self._head_end = ExtensionEnd()
        self._head_end.set_child_of(self)
        self._tail_end = ExtensionEnd()
        self._tail_end.set_child_of(self)
        self.set(has_head=1, head_a=15, head_b=15, head_c=10, head_d=10,
                 head_fill_color=diacanvas.color(0,0,0,255))

    def save (self, save_func):
        RelationshipItem.save(self, save_func)
        if self._head_end.subject:
            save_func('head_subject', self._head_end.subject)
        if self._tail_end.subject:
            save_func('tail_subject', self._tail_end.subject)

    def load (self, name, value):
        # end_head and end_tail were used in an older Gaphor version
        if name in ( 'head_end', 'head_subject' ):
            #type(self._head_end).subject.load(self._head_end, value)
            self._head_end.load('subject', value)
        elif name in ( 'tail_end', 'tail_subject' ):
            #type(self._tail_end).subject.load(self._tail_end, value)
            self._tail_end.load('subject', value)
        else:
            RelationshipItem.load(self, name, value)

    def postload(self):
        RelationshipItem.postload(self)
        self._head_end.postload()
        self._tail_end.postload()

    def do_set_property (self, pspec, value):
        if pspec.name == 'head-subject':
            self._head_end.subject = value
        elif pspec.name == 'tail-subject':
            self._tail_end.subject = value
        else:
            RelationshipItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'head':
            return self._head_end
        if pspec.name == 'tail':
            return self._tail_end
        elif pspec.name == 'head-subject':
            return self._head_end.subject
        elif pspec.name == 'tail-subject':
            return self._tail_end.subject
        else:
            return RelationshipItem.do_get_property(self, pspec)

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

        RelationshipItem.on_update(self, affine)

        self.update_child(self._head_end, affine)
        self.update_child(self._tail_end, affine)

        # bounds calculation
        b1 = self.bounds
        b2 = self._head_end.get_bounds(self._head_end.affine)
        b3 = self._tail_end.get_bounds(self._tail_end.affine)
        self.set_bounds((min(b1[0], b2[0], b3[0]), min(b1[1], b2[1], b3[1]),
                         max(b1[2], b2[2], b3[2]), max(b1[3], b2[3], b3[3])))
                    
    # Gaphor Connection Protocol

    def allow_connect_handle(self, handle, connecting_to):
        """This method is called by a canvas item if the user tries to connect
        this object's handle. allow_connect_handle() checks if the line is
        allowed to be connected. In this case that means that one end of the
        line should be connected to a Class or Actor.
        Returns: TRUE if connection is allowed, FALSE otherwise.
        """
        # TODO: Should allow to connect to Class and Actor.
        #log.debug('ExtensionItem.allow_connect_handle')
        handles = self.handles
        if handle is handles[0] \
           and isinstance(connecting_to.subject, UML.Class) \
           and connecting_to is not handles[-1].connected_to:
            return True
        elif handle is handles[-1] \
           and isinstance(connecting_to.subject, UML.Stereotype) \
           and connecting_to is not handles[0].connected_to:
            return True
        return False

    def confirm_connect_handle (self, handle):
        """This method is called after a connection is established. This method
        sets the internal state of the line and updates the data model.
        """
        #log.debug('ExtensionItem.confirm_connect_handle')

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
            Extension = UML.Extension
            for assoc in gaphor.resource(UML.ElementFactory).itervalues():
                if isinstance(assoc, Extension):
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
                element_factory = gaphor.resource(UML.ElementFactory)
                relation = element_factory.create(UML.Extension)
                head_end = element_factory.create(UML.Property)
                tail_end = element_factory.create(UML.ExtensionEnd)
                relation.package = self.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                relation.ownedEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                tail_type.ownedAttribute = head_end
                head_end.name = 'baseClass'

                self.subject = relation
                self._head_end.subject = head_end
                self._tail_end.subject = tail_end
            # Update the stereotype definition of the class. This is needed because
            # It's extension property is derived and can not send notifications.
            c1.update_stereotype()

    def confirm_disconnect_handle (self, handle, was_connected_to):
        #log.debug('ExtensionItem.confirm_disconnect_handle')
        if self.subject:
            # First delete the Property's at the ends, otherwise they will
            # be interpreted as attributes.
            self._head_end.set_subject(None)
            self._tail_end.set_subject(None)
            self.set_subject(None)

    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the name to be removed.'''
        return 1

    def on_groupable_iter(self):
        return iter([self._head_end, self._tail_end])

    def get_popup_menu(self):
        return self.popup_menu


class ExtensionEnd(diacanvas.CanvasItem, DiagramItem):
    """An association end represents one end of an association. An association
    has two ends. An association end has two labels: one for the name and
    one for the multiplicity (and maybe one for tagged values in the future).

    An AsociationEnd has no ID, hence it will not be stored, but it will be
    recreated by the owning Extension.
    
    TODO:
    - add on_point() and let it return min(distance(_name), distance(_mult)) or
      the first 20-30 units of the line, for association end popup menu.
    """
#    __gproperties__ = {
#        'name': (gobject.TYPE_STRING, 'name', '', '', gobject.PARAM_READWRITE),
#        'mult': (gobject.TYPE_STRING, 'mult', '', '', gobject.PARAM_READWRITE)
#    }
#    __gproperties__.update(DiagramItem.__gproperties__)
    __gproperties__ = DiagramItem.__gproperties__

    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        self.set_flags(diacanvas.COMPOSITE)
        
    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def postload(self):
        DiagramItem.postload(self)

    def on_update(self, affine):
        diacanvas.CanvasItem.on_update(self, affine)

    def on_point(self, x, y):
        """Given a point (x, y) return the distance to the canvas item.
        """
        return 100000

#    def on_shape_iter(self):
#        pass

    def on_connect(self, handle):
        return False

    def on_disconnect(self, handle):
        return False


initialize_item(ExtensionItem, UML.Extension)
initialize_item(ExtensionEnd)
