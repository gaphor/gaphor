"""
Connectors and connector ends from Composite Structures and Components.

Actually only Assembly connector (see Components in UML specs) is
implemented. This is done with AssemblyConnectorItem class.
AssemblyConnectorItem uses ConnectorEndItem (see ProvidedConnectorEndItem
and RequiredConnectorEndItem classes) instances to connect to components.

Component should provide at least one interface so ProvidedConnectorEndItem
can be connected to it. If there are more than one provided interfaces,
then user can choose appropriate one from ProvidedConnectorEndItem object
menu. Above also applies for required stuff.

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

from gaphor import resource, UML
from diagramline import DiagramLine, FreeLine
from elementitem import ElementItem
from component import ComponentItem
from util import create_connector_end

from gaphor.diagram.interfaceicon import AssembledInterfaceIcon
from gaphor.diagram.rotatable import SimpleRotation
from gaphor.diagram import TextElement
from gaphor.misc import uniqueid
from gaphor.misc.meta import GObjectPropsMerge
from gaphor.diagram.groupable import GroupBase


class ConnectorEndItem(FreeLine, GroupBase):
    """
    Connector end item abstract class.

    Connector end item without subject is called free connector end item.

    Free connector has no id, too.

    Connector end item has main point. Initially free connector end item is
    put in its main point. If free connector end item is moved behind the
    main point and it is not connected to any item, then it is moved to
    main point again.

    Deriving classes should implement get_interfaces method.

    For non-abstract implementations see ProvidedConnectorEndItem and
    RequiredConnectorEndItem classes.
    """

    interface_actions = []

    popup_menu = (
        'DisconnectConnector',
        'separator',
        'Interface', interface_actions
    )

    def __init__(self, id = None, mpt = None):
        """
        Create connector end item.

        If main point is not specified then it is set to (0, 0).
        """
        FreeLine.__init__(self, id, mpt)
        GroupBase.__init__(self)

        self.set_flags(diacanvas.COMPOSITE)

        self._interface_name = TextElement('name')
        self.add(self._interface_name)


    def get_component(self):
        """
        Get component to which this connector end item is connected to or
        None.
        """
        if self._handle.connected_to:
            return self._handle.connected_to.subject
        return None


    def get_popup_menu(self):
        """
        Return pop up menu for connector end item, so an user can
        - disconnect from component
        - choose an interface, which assembly connector should be connected
          to
        """
        from itemactions import ApplyInterfaceAction, register_action
        if self._handle.connected_to:
            del self.interface_actions[:]
            for interface in self.get_interfaces():
                action = ApplyInterfaceAction(interface)
                register_action(action, 'ItemFocus')
                self.interface_actions.append(action.id)
            return self.popup_menu
        else:
            return None


    def save(self, save_func):
        """
        Save handle position, main point and reference to connected item.
        """
        FreeLine.save(self, save_func)
        save_func('handle-position', self._handle.get_pos_w())
        save_func('main-point', self._main_point)
        save_func('connected-to', self._handle.connected_to, True)


    def postload(self):
        """
        Establish real connection between connector end item and connected
        item after loading diagram.
        """
        if hasattr(self, '_load_connected_to'):
            self._load_connected_to.connect_handle(self._handle)
            del self._load_connected_to
        FreeLine.postload(self)


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
            self._main_point = eval(value)
        elif name == 'connected-to':
            self._load_connected_to = value
        else:
            FreeLine.load(self, name, value)


    def on_handle_motion(self, handle, x, y, event_mask):
        """
        Control handle position. If handle position is near the main point,
        then it is moved to main point.
        
        This allows user to easily move handle to main point.
        """
        if handle is self._handle:
            mpt = self._main_point

            x, y = self.affine_point_w2i(x, y)

            if abs(mpt[0] - x) < 10 and abs(mpt[1] - y) < 10:
                x, y = mpt
            return self.affine_point_i2w(x, y)
        else:
            return FreeLine.on_handle_motion(self, handle, x, y, event_mask)


    def on_update(self, affine):
        """
        Draw line between main point and current position.
        """
        def get_pos_centered(p1, p2, width, height):
            x = p1[0] > p2[0] and width + 2 or -2
            x = (p1[0] + p2[0]) / 2.0 - x
            y = p1[1] <= p2[1] and height or 0
            y = (p1[1] + p2[1]) / 2.0 - y
            return x, y

        # move handle to main point if there is no component
        # associated with this connector end item
        if not self.is_focused() and not self.subject:
            self._handle.set_pos_i(self._main_point[0], self._main_point[1])

        pos = self._handle.get_pos_i()
        w, h = self._interface_name.get_size()
        x, y = get_pos_centered(self._main_point, pos, w, h)
        self._interface_name.update_label(x, y)

        FreeLine.on_update(self, affine)
        GroupBase.on_update(self, affine)


    def on_subject_notify(self, pspec, notifiers=()):
        """
        Generate an id when subject is set or set id to None if there is no
        subject.
        """
        FreeLine.on_subject_notify(self, pspec, notifiers)
        if self.subject and not self._id:
            self._id = uniqueid.generate_id()

        if self.subject:
            self._interface_name.subject = self.subject

            # kill connector end item if interface is no longer provided
            # or required by component
            component = self.get_component()
            component.connect('clientDependency', self.on_component_change)

        else:
            self._interface_name.subject = None
            self._id = None

        self.request_update()


    def allow_connect_handle(self, handle, item):
        """
        Allow to connect to components only and if they require or provide
        at least one interface.
        """
        return isinstance(item, ComponentItem) \
            and len(self.get_interfaces(item.subject)) > 0


    def confirm_connect_handle(self, handle):
        """
        Set first interface as subject of item.
        """
        if not self.subject:
            assert len(self.get_interfaces()) > 0
            self.set_subject(self.get_interfaces()[0])


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


    def on_component_change(self, component, data):
        """
        Kill connector end item if interface is no longer in component
        environment.
        """
        if self.subject:
            if self.subject not in self.get_interfaces():
                self.unlink()



class ProvidedConnectorEndItem(ConnectorEndItem):
    """
    Connector end item which allows to connect to components, which provide
    interfaces.
    """
    def get_interfaces(self, component = None):
        """
        Get component provided interfaces.
        """
        if not component:
            component = self.get_component()
        return component.provided



class RequiredConnectorEndItem(ConnectorEndItem):
    """
    Connector end item which allows to connect to components, which require
    interfaces.
    """
    def get_interfaces(self, component = None):
        """
        Get component required interfaces.
        """
        if not component:
            component = self.get_component()
        return component.required



class AssemblyConnectorItem(ElementItem, SimpleRotation, GroupBase):
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
        GroupBase.__init__(self)
        ElementItem.__init__(self, id)
        SimpleRotation.__init__(self)

        self._assembly = AssembledInterfaceIcon(self)

        for h in self.handles:
            h.props.movable = False

        self.set(width = self._assembly.width,
            height = self._assembly.height)


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


    def update_end_main_point(self, old_rmpt, old_pmpt):
        rmpt, pmpt = self.get_end_pos()
        for c in self.children:
            if c._main_point == old_rmpt:
                c._main_point = rmpt
            elif c._main_point == old_pmpt:
                c._main_point = pmpt


    def save(self, save_func):
        """
        Save non-free connector end items.
        """
        ElementItem.save(self, save_func)
        for c in self.children: 
            if c.subject:
                save_func(None, c)


    def load(self, name, value):
        """
        Change free connector end items position after direction update.
        """
        if name == 'dir':
            old_rmpt, old_pmpt = self.get_end_pos()
            ElementItem.load(self, name, value)
            self.update_end_main_point(old_rmpt, old_pmpt)
        else:
            ElementItem.load(self, name, value)



    def rotate(self, step = 1):
        """
        Rotate assembly connector icon and set appropriate main point
        of connector end items.
        """
        old_rmpt, old_pmpt = self.get_end_pos()
        SimpleRotation.rotate(self, step)
        self.update_end_main_point(old_rmpt, old_pmpt)

        self.request_update()


    def create_end(self, cls, mpt):
        """
        Create new connector end item.

        Connector end item is added using canvas groupable interface.
        """
        c = cls(mpt = mpt)
        self.add(c)
        return c


    def on_update(self, affine):
        """
        Update assembly connector and its connector end items.

        Maintain also free connector end items, so there is always two of
        them, one per main point kind (provided/required).
        """
        self._assembly.update_icon()

        rmpt = self._assembly.get_required_pos_i()
        pmpt = self._assembly.get_provided_pos_i()

        # store free connector end items by main point
        free_ends = {
            rmpt: set(),
            pmpt: set(),
        }

        for c in self.children:
            # store free conector end items; checking for id and subject is
            # important during diagram load
            if not c.id and not c.subject:
                free_ends[c._main_point].add(c)

        self.update_free_ends(free_ends, ProvidedConnectorEndItem, pmpt, affine)
        self.update_free_ends(free_ends, RequiredConnectorEndItem, rmpt, affine)

        ElementItem.on_update(self, affine)
        GroupBase.on_update(self, affine)


    def update_free_ends(self, free_ends, cls, mpt, affine):
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
                if c._handle.get_pos_i() != c._main_point:
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
            c = self.create_end(cls, mpt)
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
#            connector = self.relationship
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

# vim:sw=4:et
