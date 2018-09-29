"""
Connector adapters.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""
from __future__ import print_function

from zope import interface, component
from logging import getLogger

from gaphas import geometry

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram import items

logger = getLogger('Connector')


class AbstractConnect(object):
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
    interface.implements(IConnect)

    element_factory = inject('element_factory')


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

        Returns `True` by default.
        """
        iface = self.element
        if isinstance(iface, items.InterfaceItem) and iface.folded:
            canvas = self.canvas
            count = any(canvas.get_connections(connected=iface))
            return not count and isinstance(self.line, (items.DependencyItem, items.ImplementationItem))
        return True


    def connect(self, handle, port):
        """
        Connect to an element. Note that at this point the line may
        be connected to some other, or the same element.
        Also the connection at UML level still exists.
        
        Returns `True` if a connection is established.
        """
        return True


#    def reconnect(self, handle, port):
#        """
#        UML model reconnection method.
#        """
#        raise NotImplementedError('Reconnection not implemented')


    def disconnect(self, handle):
        """
        Disconnect UML model level connections.
        """
        pass



class CommentLineElementConnect(AbstractConnect):
    """
    Connect a comment line to any element item.
    """
    component.adapts(items.ElementItem, items.CommentLineItem)

    def allow(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        connected_to = self.get_connected(opposite)
        element = self.element

        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # One end should be connected to a CommentItem:
        cls = items.CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        # Do not allow to links between the comment and the element
        if connected_to and element and \
                ((isinstance(connected_to.subject, UML.Comment) and \
                    self.element.subject in connected_to.subject.annotatedElement) or \
                 (isinstance(self.element.subject, UML.Comment) and \
                    connected_to.subject in self.element.subject.annotatedElement)):
            return None

        return super(CommentLineElementConnect, self).allow(handle, port)

    def connect(self, handle, port):
        if super(CommentLineElementConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            connected_to = self.get_connected(opposite)
            if connected_to:
                if isinstance(connected_to.subject, UML.Comment):
                    connected_to.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            logger.debug('Disconnecting %s and %s' % (hct, oct))
            try:
                if hct.subject and isinstance(oct.subject, UML.Comment):
                    del oct.subject.annotatedElement[hct.subject]
                elif hct.subject and oct.subject:
                    del hct.subject.annotatedElement[oct.subject]
            except ValueError:
                logger.debug('Invoked CommentLineElementConnect.disconnect() for nonexistant relationship')
                
        super(CommentLineElementConnect, self).disconnect(handle)

component.provideAdapter(CommentLineElementConnect)


class CommentLineLineConnect(AbstractConnect):
    """
    Connect a comment line to any diagram line.
    """
    component.adapts(items.DiagramLine, items.CommentLineItem)

    def allow(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = self.get_connected(opposite)

        # do not connect to the same item nor connect to other comment line
        if connected_to is element or not element.subject or \
                isinstance(element, items.CommentLineItem):
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        print('Connecting', element, 'with', element.subject)

        # One end should be connected to a CommentItem:
        cls = items.CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineLineConnect, self).allow(handle, port)

    def connect(self, handle, port):
        if super(CommentLineLineConnect, self).connect(handle, port):
            opposite = self.line.opposite(handle)
            c = self.get_connected(opposite)
            if c and self.element.subject:
                if isinstance(c.subject, UML.Comment):
                    c.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = c.subject

    def disconnect(self, handle):
        c1 = self.get_connected(handle)
        opposite = self.line.opposite(handle)
        c2 = self.get_connected(opposite)
        if c1 and c2:
            if isinstance(c1.subject, UML.Comment):
                del c1.subject.annotatedElement[c2.subject]
            elif c2.subject:
                del c2.subject.annotatedElement[c1.subject]
        super(CommentLineLineConnect, self).disconnect(handle)

component.provideAdapter(CommentLineLineConnect)


class UnaryRelationshipConnect(AbstractConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    Unary relationships are allowed to connect both ends to the same element

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

    element_factory = inject('element_factory')


    def relationship(self, required_type, head, tail):
        """
        Find an existing relationship in the model that meets the
        required type and is connected to the same model element the head
        and tail of the line are conncted to.

        type - the type of relationship we're looking for
        head - tuple (association name on line, association name on element)
        tail - tuple (association name on line, association name on element)
        """
        line = self.line

        head_subject = self.get_connected(line.head).subject
        tail_subject = self.get_connected(line.tail).subject

        # First check if the right subject is already connected:
        if line.subject \
           and getattr(line.subject, head.name) is head_subject \
           and getattr(line.subject, tail.name) is tail_subject:
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
        Like relation(), but create a new instance of none was found.
        """
        relation = self.relationship(type, head, tail)
        if not relation:
            line = self.line
            relation = self.element_factory.create(type)
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
            raise ValueError('Incorrect handle passed to adapter')


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
            adapter = component.queryMultiAdapter((line, cinfo.connected), IConnect)
            assert adapter
            adapter.connect(cinfo.handle, cinfo.port)
        
    def disconnect_connected_items(self):
        """
        Cause items connected to @line to be disconnected.
        This is nessesary if the subject of the @line is to be removed.

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
            adapter = component.queryMultiAdapter((cinfo.item, cinfo.connected), IConnect)
            assert adapter
            adapter.disconnect(cinfo.handle)
        return connections

    def connect_subject(self, handle):
        """
        Establish the relationship at model level.
        """
        raise NotImplementedError, 'Implement connect_subject() in a subclass'

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
            old = line.subject
             
            connections = self.disconnect_connected_items()
            
            self.disconnect_subject(handle)
            if old:
                self.connect_connected_items(connections)

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

        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        return super(RelationshipConnect, self).allow(handle, port)


# vim:sw=4:et:ai
