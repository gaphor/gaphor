"""
Connectors and connector ends from Composite Structures and Components.

Assembly connector (see Components in UML specs) is implemented with
AssemblyConnectorItem class.  Connector class implements normal connector
(see Composite Structures) and delegation connector (see Components).


UML Specificatiom Issues
========================
In some areas UML specification is not clear about connector kind and
interfaces as connectable elements, see also

    http://modeldrivenengineering.org/bin/view/Umlrtf/CurrentProposals

Connector Kind
----------------------------------
Components chapter adds kind attribute to connector class. According to UML
specs it is enumeration with two possible values 'assembly' and
'delegation'.

This is an issue for connector between connectable elements like
properties, parameters or more specific ports not characterized by
interfaces. It is not clear what value should be assigned for connector
kind for connectors between such elements.


Interfaces as Connectable Elements
----------------------------------
Composite Structures chapter in UML Superstructure (formal 05/07/04)
document does not specify interfaces as connectable elements.

But definition of assembly connector says:

    An assembly connector is a connector between two components that
    defines that one component provides the services that another component
    requires. An assembly connector is a connector that is defined from a
    required _interface_ or port to a provided _interface_ or port

Therefore, code of connectors is written with assumption, that interfaces
are connectable elements.

This is subject to change in the future when UML specification clarifies in
this area.
"""

import diacanvas
from gaphor import resource, UML
from gaphor.diagram import initialize_item
from diagramline import DiagramLine
from diagramitem import DiagramItem
from elementitem import ElementItem
from util import create_connector_end
from gaphor.diagram.interfaceicon import AssembledInterfaceIcon
from gaphor.diagram.rotatable import SimpleRotation
from gaphor.misc import uniqueid
from gaphor.misc.meta import GObjectPropsMerge

class ConnectorEndItem(diacanvas.CanvasItem, DiagramItem):
    """
    Connector end item.

    Connector end item without subject is called free connector end item.

    Free connector has no id, too.

    Connector end item has main point. Initially free connector end item is
    put in its main point. If free connector end item is moved behind the
    main point and it is not connected to any item, then it is moved to
    main point again.
    """
    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    popup_menu = (
        'EditDelete',
    )

    def __init__(self, id = None, mpt = None):
        """
        Create connector end item.

        If main point is not specified then it is set to (0, 0).
        """
        diacanvas.CanvasItem.__init__(self)
        DiagramItem.__init__(self, id)

        self.set_flags(diacanvas.COMPOSITE)

        self._mpt = mpt # main point is the point where required or
                        # provided connector end item starts its life
        if self._mpt is None:
            self._mpt = 0, 0

        self._handle = diacanvas.Handle(self)
        self._handle.props.connectable = True

        self._line = diacanvas.shape.Path()
        self._line.set_line_width(2.0)


    def save(self, save_func):
        """
        Save handle position, main point and reference to connected item.
        """
        DiagramItem.save(self, save_func)
        save_func('handle-position', self._handle.get_pos_w())
        save_func('main-point', self._mpt)
        save_func('connected-to', self._handle.connected_to, True)


    def postload(self):
        """
        Establish real connection between connector end item and connected
        item.
        """
        if hasattr(self, '_load_connected_to'):
            self._load_connected_to.connect_handle(self._handle)
            del self._load_connected_to
        DiagramItem.postload(self)


    def load(self, name, value):
        """
        Load handle position, main point and reference to connected item.

        Reference to connected item is stored in ConnectorEndItem._load_connected_to.
        Real connection between connector end item and connected item is
        established in ConnectorEndItem.postload method.
        """
        if name == 'handle-position':
            x, y = eval(value)
            self._handle.set_pos_w(x, y)
        elif name == 'main-point':
            self._mpt = eval(value)
        elif name == 'connected-to':
            self._load_connected_to = value
        else:
            DiagramItem.load(self, name, value)


    def on_handle_motion(self, handle, x, y, event_mask):
        """
        Control handle position. If handle position is near the main point,
        then it is moved to main point.
        
        This allows user to easily move handle to main point.
        """
        mpt = self._mpt

        x, y = self.affine_point_w2i(x, y)

        if abs(mpt[0] - x) < 10 and abs(mpt[1] - y) < 10:
            x, y = mpt
        x, y = self.affine_point_i2w(x, y)

        return x, y


    def on_update(self, affine):
        """
        Draw line between main point and current position.
        """
        # move handle to main point if it is connected
        # to no item
        if not self.subject and not self.is_focused():
            self._handle.set_pos_i(self._mpt[0], self._mpt[1])

        diacanvas.CanvasItem.on_update(self, affine)

        # draw line from main point to current handle position
        x, y = self._handle.get_pos_w()
        x, y = self.affine_point_w2i(x, y)
        pos = x, y
        self._line.line((self._mpt, pos))

        self.set_bounds([min(self._mpt[0], pos[0]),
            min(self._mpt[1], pos[1]),
            max(self._mpt[0], pos[0]),
            max(self._mpt[1], pos[1])])


    def on_subject_notify(self, pspec, notifiers=()):
        """
        Generate an id when subject is set or set id to None if there is no
        subject.
        """
        DiagramItem.on_subject_notify(self, pspec, notifiers)
        if self.subject and not self._id:
            self._id = uniqueid.generate_id()
        else:
            self._id = None


    def on_shape_iter(self):
        """
        Return line drawn between main point and current position.
        """
        yield self._line


    def allow_connect_handle(self, handle, item):
        """
        Allow to connect to interfaces only. Do not allow to connect to the
        same interface item twice (still it should be possible to connect
        to the same interface several times).
        """
        allow_connection = isinstance(item.subject, UML.Interface)

        if allow_connection:
            # check if this interface item is already connected
            # with other connector end item
            for c in self.parent._ends:
                # disalow connection if other connector item end is alread
                # connected to interface
                if c != self and c._handle.connected_to == item:
                    allow_connection = False
                    break
        return allow_connection


    def confirm_connect_handle(self, handle):
        """
        Create new connector end between connectable element and connector.
        """
        if not self.subject:
            item = handle.connected_to

            connector = self.parent.subject
            end = create_connector_end(connector, item.subject)
            self.set_subject(end)
            item.request_update()


    def confirm_disconnect_handle(self, handle, item):
        """
        Remove subject.
        """
        self.set_subject(None)


    def allow_disconnect_handle(self, handle):
        """
        It is always allowed to disconnect handle.
        """
        return True



class AssemblyConnectorItem(ElementItem, SimpleRotation, diacanvas.CanvasGroupable):
    """
    Assembly connector item.

    It has exactly two free connector end items.

    Connector end items are added and removed from assembly connector using
    canvas groupable interface.

    Assembly connector item distinguishes between two kind of main points.
    One is for connector end items, which connect to provided interfaces/ports.
    Other is for required interfaces/ports.
    """

    __metaclass__ = GObjectPropsMerge # merge properties from SimpleRotation

    popup_menu = (
        'EditDelete',
        'separator',
        'Rotate',
    )

    def __init__(self, id):
        """
        Create assembly connector item.
        """
        ElementItem.__init__(self, id)
        SimpleRotation.__init__(self, id)

        self._assembly = AssembledInterfaceIcon(self)

        for h in self.handles:
            h.props.movable = False

        self.set(width = self._assembly.width,
            height = self._assembly.height)

        self._ends = set() # connector end items


    def do_set_property(self, pspec, value):
        if pspec.name in SimpleRotation.__gproperties__:
            SimpleRotation.do_set_property(self, pspec, value)
        else:
            ElementItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name in SimpleRotation.__gproperties__:
            return SimpleRotation.do_get_property(self, pspec)
        else:
            return ElementItem.do_get_property(self, pspec)


    def get_end_pos(self):
        return self._assembly.get_required_pos_i(), \
            self._assembly.get_provided_pos_i()


    def update_end_mpt(self, old_rmpt, old_pmpt):
        rmpt, pmpt = self.get_end_pos()
        for c in self._ends:
            if c._mpt == old_rmpt:
                c._mpt = rmpt
            elif c._mpt == old_pmpt:
                c._mpt = pmpt


    def save(self, save_func):
        """
        Save non-free connector end items.
        """
        ElementItem.save(self, save_func)
        for c in self._ends: 
            if c.subject:
                save_func(None, c)


    def load(self, name, value):
        """
        Change free connector end items position after direction update.
        """
        if name == 'dir':
            old_rmpt, old_pmpt = self.get_end_pos()
            ElementItem.load(self, name, value)
            self.update_end_mpt(old_rmpt, old_pmpt)
        else:
            ElementItem.load(self, name, value)



    def rotate(self, step = 1):
        """
        Rotate assembly connector icon and set appropriate main point
        of connector end items.
        """
        old_rmpt, old_pmpt = self.get_end_pos()
        SimpleRotation.rotate(self, step)
        self.update_end_mpt(old_rmpt, old_pmpt)

        self.request_update()


    def create_end(self, mpt):
        """
        Create new connector end item.

        Connector end item is added using canvas groupable interface.
        """
        c = ConnectorEndItem(mpt = mpt)
        self.add(c)
        return c


    def on_update(self, affine):
        """
        Update assemble connector and its connector end items.

        Maintain also free connector end items, so there is always two of
        them. One per main point kind (provided/required).
        """
        ElementItem.on_update(self, affine)

        self._assembly.update_icon()

        rmpt = self._assembly.get_required_pos_i()
        pmpt = self._assembly.get_provided_pos_i()

        # store free connector end items by main point
        free_ends = {
            rmpt: set(),
            pmpt: set(),
        }

        for c in self._ends:
            self.update_child(c, affine)

            # update bounds
            x, y = c._handle.get_pos_w()
            x, y = c.affine_point_w2i(x, y)
            pos = x, y
            self.set_bounds(diacanvas.geometry.rectangle_add_point(self.get_bounds(),
                pos))

            # store free conector end items;
            # checking for connector end item id is important during load
            if not c.subject and not c._id:
                free_ends[c._mpt].add(c)

        self.update_free_ends(free_ends, pmpt, affine)
        self.update_free_ends(free_ends, rmpt, affine)


    def update_free_ends(self, free_ends, mpt, affine):
        """
        There should only one free connector end item for given main point.

        Remove these free connector end items, which are no longer
        necessary.
        
        Create free connector end item in given main point if it is
        missing.
        """
        count = len(free_ends[mpt]) 
        if count > 1:
            # leave only one free connector end item
            
            # first, remove all, which are not in main point
            to_be_removed = list(free_ends[mpt])
            for c in to_be_removed:
                if c._handle.get_pos_i() != c._mpt:
                    c.unlink()
                    free_ends[mpt].remove(c)

            # now, leave only one connector end item in main point
            to_be_removed = list(free_ends[mpt])
            if len(to_be_removed) > 1:
                for c in to_be_removed[1:]:
                    c.unlink()
                    free_ends[mpt].remove(c)

            # finally, we should have one free connector end item in given main point
            assert len(free_ends[mpt]) == 1

        elif count == 0:
            # if there is no free connector end items, then create one
            c = self.create_end(mpt)
            self.update_child(c, affine)


    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Set appropriate value of connector kind attribute. This is
        'assembly', of course.
        """
        ElementItem.on_subject_notify(self, pspec, notifiers)
        if self.subject:
            self.subject.kind = 'assembly'
        log.debug('creating assembly connector')


    def on_shape_iter(self):
        """
        Return assembled interface icon as a shape.
        """
        return self._assembly.on_shape_iter()


    #
    # groupable
    #

    def on_groupable_iter(self):
        """
        Return connector end items.
        """
        return iter(self._ends)


    def on_groupable_add(self, item):
        """
        Add connector end item.
        """
        self._ends.add(item)
        item.set_child_of(self)
        return True


    def on_groupable_remove(self, item):
        """
        Remove connector end item.
        """
        assert item in self._ends
        self._ends.remove(item)
        item.set_child_of(None)
        return True



class ConnectorItem(DiagramLine):
    pass
#    """
#    todo: ports
#    """
#    
#    def __init__(self, id=None):
#        DiagramLine.__init__(self, id)
#
#
#    def find_relationship(self, head_subject, tail_subject):
#        print "zz", head_subject, tail_subject
#
#
#    def allow_connect_handle(self, handle, connecting_to):
#        return True
#        return isinstance(connecting_to.subject, UML.Interface)
#
#
#    def confirm_connect_handle (self, handle):
#        c1 = self.handles[0].connected_to
#        c2 = self.handles[-1].connected_to
#        if c1 and c2:
#            s1 = c1.subject
#            s2 = c2.subject
#            print s1.end
#            print s2.end
#            connector = self.find_relationship(s1, s2)
#            if not connector:
#                connector = resource(UML.ElementFactory).create(UML.Connector)
#                connector.kind = 'assembly'
#                create_connector_end(connector, s1)
#                create_connector_end(connector, s2)
#                
#            self.subject = connector
#
#
#    def confirm_disconnect_handle(self, handle, was_connected_to):
#        if self.subject:
#            if __debug__:
#                end1, end2 = tuple(self.subject.end)
#                assert len(end1.role.end) > 0
#                assert len(end2.role.end) > 0
#            self.set_subject(None)
#            if __debug__:
#                assert end1.role is None
#                assert end2.role is None
#
#
#    def is_assembly(self):
#        c1 = self.handles[0].connected_to
#        c2 = self.handles[-1].connected_to
#        return c1 and c2 \
#            and isinstance(c1.subject, UML.Interface) \
#            and isinstance(c2.subject, UML.Interface)
#
#
#    def on_update(self, affine):
#        DiagramLine.on_update(self, affine)
#        x1, y1 = self.handles[0].get_pos_i()
#        x2, y2 = self.handles[-1].get_pos_i()
#        x = (x1 + x2) / 2
#        y = (y1 + y2) / 2
#        if self.is_assembly():
#            self._assembly.line(_required_arcs[3])
#            #self._assembly.set_pos((x, y))
#
#
#    def on_shape_iter(self):
#        if self.is_assembly():
#            return iter([self._assembly])
#        else:
#            return DiagramLine.on_shape_iter(self)


initialize_item(ConnectorItem)
initialize_item(ConnectorEndItem)
initialize_item(AssemblyConnectorItem)

# vim:sw=4:et
