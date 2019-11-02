"""
Connector adapters.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import annotations

from typing import List, Optional, Type, TypeVar, Union, TYPE_CHECKING

from gaphas.canvas import Connection
from gaphas.connector import Handle, Port

from gaphor import UML
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.misc.generic.multidispatch import multidispatch, FunctionDispatcher

if TYPE_CHECKING:
    from gaphor.UML.properties import association, umlproperty, relation_one


T = TypeVar("T", bound=UML.Element)


class ConnectBase:
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    def __init__(self, item: ElementPresentation, line_item: LinePresentation):
        self.item = item
        self.line_item = line_item

    def allow(self, handle: Handle, port: Port) -> bool:
        """
        Determine if a connection is allowed.

        Do some extra checks to see if the items actually can be connected.
        """
        return False

    def connect(self, handle: Handle, port: Port) -> bool:
        """
        Connect a line's handle to element.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """
        raise NotImplementedError(f"No connector for {self.item} and {self.line_item}")

    def disconnect(self, handle: Handle) -> None:
        """
        The true disconnect. Disconnect a handle.connected_to from an
        element. This requires that the relationship is also removed at
        model level.
        """
        raise NotImplementedError(f"No connector for {self.item} and {self.line_item}")


# Work around issue https://github.com/python/mypy/issues/3135 (Class decorators are not type checked)
# This definition, along with the the ignore below, seems to fix the behaviour for mypy at least.
IConnect: FunctionDispatcher[Type[ConnectBase]] = multidispatch(object, object)(
    ConnectBase
)


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

    def __init__(
        self,
        element: ElementPresentation[UML.Element],
        line: LinePresentation[UML.Element],
    ) -> None:
        assert element.canvas == line.canvas
        self.element = element
        self.line = line
        self.canvas = element.canvas

    def get_connection(self, handle: Handle) -> Optional[Connection]:
        """
        Get connection information
        """
        assert self.canvas
        return self.canvas.get_connection(handle)

    def get_connected(self, handle: Handle) -> Optional[UML.Presentation]:
        """
        Get item connected to a handle.
        """
        assert self.canvas
        cinfo = self.canvas.get_connection(handle)
        if cinfo:
            return cinfo.connected  # type: ignore
        return None

    def get_connected_port(self, handle: Handle) -> Optional[Port]:
        """
        Get port of item connected to connecting item via specified handle.
        """
        assert self.canvas
        cinfo = self.canvas.get_connection(handle)
        if cinfo:
            return cinfo.port
        return None

    def allow(self, handle: Handle, port: Port) -> bool:
        """
        Determine if items can be connected.

        The method contains a hack for folded interfaces, see
        `gaphor.diagram.classes.interface` module documentation for
        connection to folded interface rules.

        Returns `True` if connection is allowed.
        """
        return True

    def connect(self, handle: Handle, port: Port) -> bool:
        """
        Connect to an element. Note that at this point the line may
        be connected to some other, or the same element.
        Also the connection at UML level still exists.

        Returns `True` if a connection is established.
        """
        return True

    def disconnect(self, handle: Handle) -> None:
        """Disconnect UML model level connections."""


class UnaryRelationshipConnect(AbstractConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    Unary relationships are allowed to connect both ends to the same element

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

    def relationship(
        self, required_type: Type[UML.Element], head: relation_one, tail: relation_one
    ) -> Optional[UML.Element]:
        """
        Find an existing relationship in the model that meets the
        required type and is connected to the same model element the head
        and tail of the line are connected to.

        type - the type of relationship we're looking for
        head - tuple (association name on line, association name on element)
        tail - tuple (association name on line, association name on element)
        """
        line = self.line

        line_head = self.get_connected(line.head)
        line_tail = self.get_connected(line.tail)
        assert line_head
        assert line_tail
        head_subject = line_head.subject
        tail_subject = line_tail.subject

        # First check if the right subject is already connected:
        if (
            line.subject
            and getattr(line.subject, head.name) is head_subject
            and getattr(line.subject, tail.name) is tail_subject
        ):
            return line.subject

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        assert tail.opposite, f"Tail end of {line} has no opposite definition"
        for gen in getattr(tail_subject, tail.opposite):  # type: UML.Element
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
            item: Union[ElementPresentation, LinePresentation]
            for item in gen.presentation:  # type: ignore
                # Allow line to be returned. Avoids strange
                # behaviour during loading
                if item.canvas is line.canvas and item is not line:
                    break
            else:
                return gen
        return None

    def relationship_or_new(
        self, type: Type[T], head: relation_one, tail: relation_one
    ) -> T:
        """
        Like relation(), but create a new instance if none was found.
        """
        relation = self.relationship(type, head, tail)
        if not relation:
            line = self.line
            relation = line.model.create(type)
            line_head = self.get_connected(line.head)
            line_tail = self.get_connected(line.tail)
            assert line_head
            assert line_tail
            setattr(relation, head.name, line_head.subject)
            setattr(relation, tail.name, line_tail.subject)
        assert isinstance(relation, type)
        return relation

    def reconnect_relationship(
        self, handle: Handle, head: relation_one, tail: relation_one
    ) -> None:
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
        assert c1
        assert c2
        if line.head is handle:
            setattr(line.subject, head.name, c1.subject)
        elif line.tail is handle:
            setattr(line.subject, tail.name, c2.subject)
        else:
            raise ValueError("Incorrect handle passed to adapter")

    def connect_connected_items(self, connections: None = None) -> None:
        """
        Cause items connected to ``line`` to reconnect, allowing them to
        establish or destroy relationships at model level.
        """
        assert self.canvas

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

    def disconnect_connected_items(self) -> List[Connection]:
        """
        Cause items connected to @line to be disconnected.
        This is necessary if the subject of the @line is to be removed.

        Returns a list of (item, handle) pairs that were connected (this
        list can be used to connect items again with connect_connected_items()).
        """
        assert self.canvas

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

    def connect_subject(self, handle: Handle) -> bool:
        """
        Establish the relationship at model level.
        """
        raise NotImplementedError("Implement connect_subject() in a subclass")

    def disconnect_subject(self, handle: Handle) -> None:
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

    def connect(self, handle: Handle, port: Port) -> bool:
        """
        Connect the items to each other. The model level relationship
        is created by create_subject()
        """
        if super().connect(handle, port):
            opposite = self.line.opposite(handle)
            oct = self.get_connected(opposite)
            if oct:
                self.connect_subject(handle)
                line = self.line
                if line.subject:
                    self.connect_connected_items()
            return True
        return False

    def disconnect(self, handle: Handle) -> None:
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

        super().disconnect(handle)


class RelationshipConnect(UnaryRelationshipConnect):
    """
    """

    def allow(self, handle: Handle, port: Port) -> bool:
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
            return False

        # Same goes for subjects:
        if (
            connected_to
            and (not (connected_to.subject or element.subject))
            and connected_to.subject is element.subject
        ):
            return False

        return super().allow(handle, port)
