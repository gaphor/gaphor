"""
Connector adapters.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

import abc

from gaphor import UML
from gaphor.misc.generic.multidispatch import multidispatch


class ConnectBase(metaclass=abc.ABCMeta):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    @abc.abstractmethod
    def allow(self, handle, port):
        """
        Determine if a connection is allowed.

        Do some extra checks to see if the items actually can be connected.
        """

    @abc.abstractmethod
    def connect(self, handle, port):
        """
        Connect a line's handle to element.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """

    @abc.abstractmethod
    def disconnect(self, handle):
        """
        The true disconnect. Disconnect a handle.connected_to from an
        element. This requires that the relationship is also removed at
        model level.
        """


@multidispatch(object, object)
class IConnect(ConnectBase):
    """
    This function is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def __init__(self, item, line_item):
        self.item = item
        self.line_item = line_item

    def allow(self, handle, port):
        return False

    def connect(self, handle, port):
        raise NotImplementedError(f"No connector for {self.item} and {self.line_item}")

    def disconnect(self, handle):
        raise NotImplementedError(f"No connector for {self.item} and {self.line_item}")


class AbstractConnect(ConnectBase):
    """
    Connection adapter for Gaphor diagram items.

    Line item ``line`` connects with a handle to a connectable item ``element``.

    Attributes:

    - line: connecting item
    - element: connectable item

    The following methods are required to make this work:

    - `allow()`: is the connection allowed at all (during mouse movement for example).
    - `connect()`: Establish a connection between element and line. Also takes care of
      disconnects, if required (e.g. 1:1 relationships)
    - `disconnect()`: Break connection, called when dropping a handle on a
       point where it can not connect.
    - `reconnect()`: Connect to another item (only used if present)

    By convention the adapters are registered by (element, line) -- in that order.

    """

    def __init__(self, element, line):
        self.element = element
        self.line = line
        self.canvas = self.element.canvas
        assert self.canvas == self.element.canvas == self.line.canvas

    def get_connection(self, handle):
        """
        Get connection information
        """
        return self.canvas.get_connection(handle)

    def get_connected(self, handle):
        """
        Get item connected to a handle.
        """
        cinfo = self.canvas.get_connection(handle)
        if cinfo is not None:
            return cinfo.connected

    def get_connected_port(self, handle):
        """
        Get port of item connected to connecting item via specified handle.
        """
        cinfo = self.canvas.get_connection(handle)
        if cinfo is not None:
            return cinfo.port

    def allow(self, handle, port):
        """
        Determine if items can be connected.

        The method contains a hack for folded interfaces, see
        `gaphor.diagram.classes.interface` module documentation for
        connection to folded interface rules.

        Returns `True` if connection is allowed.
        """
        from gaphor.diagram.classes.interface import InterfaceItem
        from gaphor.diagram.classes.implementation import ImplementationItem
        from gaphor.diagram.classes.dependency import DependencyItem

        iface = self.element
        if isinstance(iface, InterfaceItem) and iface.folded:
            canvas = self.canvas
            count = any(canvas.get_connections(connected=iface))
            return not count and isinstance(
                self.line, (DependencyItem, ImplementationItem)
            )
        return True

    def connect(self, handle, port):
        """
        Connect to an element. Note that at this point the line may
        be connected to some other, or the same element.
        Also the connection at UML level still exists.

        Returns `True` if a connection is established.
        """
        return True

    def disconnect(self, handle):
        """Disconnect UML model level connections."""
        pass


class UnaryRelationshipConnect(AbstractConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    Unary relationships are allowed to connect both ends to the same element

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

    def relationship(self, required_type, head, tail):
        """
        Find an existing relationship in the model that meets the
        required type and is connected to the same model element the head
        and tail of the line are connected to.

        type - the type of relationship we're looking for
        head - tuple (association name on line, association name on element)
        tail - tuple (association name on line, association name on element)
        """
        line = self.line

        head_subject = self.get_connected(line.head).subject
        tail_subject = self.get_connected(line.tail).subject

        # First check if the right subject is already connected:
        if (
            line.subject
            and getattr(line.subject, head.name) is head_subject
            and getattr(line.subject, tail.name) is tail_subject
        ):
            return line.subject

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, tail.opposite):
            if not isinstance(gen, required_type):
                continue

            gen_head = getattr(gen, head.name)
            try:
                if not head_subject in gen_head:
                    continue
            except TypeError:
                if not gen_head is head_subject:
                    continue

            # Check for this entry on line.canvas
            for item in gen.presentation:
                # Allow line to be returned. Avoids strange
                # behaviour during loading
                if item.canvas is line.canvas and item is not line:
                    break
            else:
                return gen
        return None

    def relationship_or_new(self, type, head, tail):
        """
        Like relation(), but create a new instance if none was found.
        """
        relation = self.relationship(type, head, tail)
        if not relation:
            line = self.line
            relation = line.model.create(type)
            setattr(relation, head.name, self.get_connected(line.head).subject)
            setattr(relation, tail.name, self.get_connected(line.tail).subject)
        return relation

    def reconnect_relationship(self, handle, head, tail):
        """
        Reconnect relationship for given handle.

        :Parameters:
         handle
            Handle at which reconnection happens.
         head
            Relationship head attribute name.
         tail
            Relationship tail attribute name.
        """
        line = self.line
        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if line.head is handle:
            setattr(line.subject, head.name, c1.subject)
        elif line.tail is handle:
            setattr(line.subject, tail.name, c2.subject)
        else:
            raise ValueError("Incorrect handle passed to adapter")

    def connect_connected_items(self, connections=None):
        """
        Cause items connected to ``line`` to reconnect, allowing them to
        establish or destroy relationships at model level.
        """
        line = self.line
        canvas = self.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        for cinfo in connections or canvas.get_connections(connected=line):
            if line is cinfo.connected:
                continue
            adapter = IConnect(line, cinfo.connected)
            assert adapter, "No element to connect {} and {}".format(
                line, cinfo.connected
            )
            adapter.connect(cinfo.handle, cinfo.port)

    def disconnect_connected_items(self):
        """
        Cause items connected to @line to be disconnected.
        This is necessary if the subject of the @line is to be removed.

        Returns a list of (item, handle) pairs that were connected (this
        list can be used to connect items again with connect_connected_items()).
        """
        line = self.line
        canvas = self.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        connections = list(canvas.get_connections(connected=line))
        for cinfo in connections:
            adapter = IConnect(cinfo.item, cinfo.connected)
            adapter.disconnect(cinfo.handle)
        return connections

    def connect_subject(self, handle):
        """
        Establish the relationship at model level.
        """
        raise NotImplementedError("Implement connect_subject() in a subclass")

    def disconnect_subject(self, handle):
        """
        Disconnect the diagram item from its model element. If there are
        no more presentations(diagram items) connected to the model element,
        unlink() it too.
        """
        line = self.line
        old = line.subject
        del line.subject
        if old and len(old.presentation) == 0:
            old.unlink()

    def connect(self, handle, port):
        """
        Connect the items to each other. The model level relationship
        is created by create_subject()
        """
        if super(UnaryRelationshipConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            oct = self.get_connected(opposite)
            if oct:
                self.connect_subject(handle)
                line = self.line
                if line.subject:
                    self.connect_connected_items()
            return True

    def disconnect(self, handle):
        """
        Disconnect model element.
        """
        line = self.line
        opposite = line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            # Both sides of line are connected => disconnect
            connections = self.disconnect_connected_items()
            self.disconnect_subject(handle)

        super(UnaryRelationshipConnect, self).disconnect(handle)


class RelationshipConnect(UnaryRelationshipConnect):
    """
    """

    def allow(self, handle, port):
        """
        In addition to the normal check, both relationship ends may not be
        connected to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = self.get_connected(opposite)

        # Element can not be a parent of itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if (
            connected_to
            and (not (connected_to.subject or element.subject))
            and connected_to.subject is element.subject
        ):
            return None

        return super(RelationshipConnect, self).allow(handle, port)
