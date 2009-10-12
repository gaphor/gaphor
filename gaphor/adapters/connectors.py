"""
Connector adapters.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from zope import interface, component

from gaphas import geometry
from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram import items


def find_closest_port(item, point, converter):
    closest = None
    max_dist = 10000
    for p in item.ports():
        if not p.connectable: continue
        ip = converter(*point)
        pg, d = p.glue(ip)
        if d >= max_dist: continue
        closest = p
        max_dist = d
    return closest


class AbstractConnect(object):
    """
    Connection adapter for Gaphor diagram items.

    Line item ``line`` connects with a handle to a connectable item ``element``.

    Attributes:

    - line: connecting item
    - element: connectable item
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


    def glue(self, handle, port):
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
        be connected to some other, or the same element by means of the
        handle.connected_to property. Also the connection at UML level
        still exists.
        
        Returns `True` if a connection is established.
        """
        return True


    def reconnect(self, handle, port):
        """
        Reconnect to an element. Note that at this point the line may
        be connected to some other, or the same element by means of the
        handle.connected_to property. Also the connection at UML level
        still exists.
        """
        pass


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

    def glue(self, handle, port):
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
            #print 'Subjects none or match:', connected_to.subject, element.subject
            return None

        # One end should be connected to a CommentItem:
        cls = items.CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineElementConnect, self).glue(handle, port)

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
            if isinstance(oct.subject, UML.Comment):
                del oct.subject.annotatedElement[hct.subject]
            elif oct.subject:
                del hct.subject.annotatedElement[oct.subject]
        super(CommentLineElementConnect, self).disconnect(handle)

component.provideAdapter(CommentLineElementConnect)


class CommentLineLineConnect(AbstractConnect):
    """
    Connect a comment line to any diagram line.
    """
    component.adapts(items.DiagramLine, items.CommentLineItem)

    def glue(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to

        # do not connect to the same item nor connect to other comment line
        if connected_to is element or isinstance(element, items.CommentLineItem):
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

        return super(CommentLineLineConnect, self).glue(handle, port)

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


class RelationshipConnect(AbstractConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

    element_factory = inject('element_factory')

    # relationships can sometimes by unary, i.e. association, flow
    # override in deriving class to allow unary relationship
    CAN_BE_UNARY = False

    def glue(self, handle, port):
        """
        In addition to the normal check, both relationship ends may not be
        connected to the same element. Same goes for subjects.
        """
        if not self.CAN_BE_UNARY:
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

        return super(RelationshipConnect, self).glue(handle, port)


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
        element = self.element

        head_subject = self.get_connected(line.head).subject
        tail_subject = self.get_connected(line.tail).subject

        edge_head_name = head[0]
        node_head_name = head[1]
        edge_tail_name = tail[0]
        node_tail_name = tail[1]

        # First check if the right subject is already connected:
        if line.subject \
           and getattr(line.subject, edge_head_name) is head_subject \
           and getattr(line.subject, edge_tail_name) is tail_subject:
            return line.subject

        # This is the type of the relationship we're looking for
        #required_type = getattr(type(tail_subject), node_tail_name).type

        # Try to find a relationship, that is already created, but not
        # yet displayed in the diagram.
        for gen in getattr(tail_subject, node_tail_name):
            if not isinstance(gen, required_type):
                continue
                
            gen_head = getattr(gen, edge_head_name)
            try:
                if not head_subject in gen_head:
                    continue
            except TypeError:
                if not gen_head is head_subject:
                    continue

            # check for this entry on line.canvas
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
            setattr(relation, head[0], self.get_connected(line.head).subject)
            setattr(relation, tail[0], self.get_connected(line.tail).subject)
        return relation

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
            port = find_closest_port(cinfo.item,
                    canvas.get_matrix_i2c(line).transform_point(*cinfo.handle.pos),
                    canvas.get_matrix_i2c(cinfo.item).transform_point)
                
            adapter = component.queryMultiAdapter((line, item), IConnect)
            assert adapter
            adapter.connect(handle, port)
        
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
            adapter = component.queryMultiAdapter((line, cinfo.item), IConnect)
            assert adapter
            adapter.disconnect(handle)
        return connections

    def connect_subject(self, handle):
        """
        Establish the relationship at model level.
        """
        raise NotImplemented, 'Implement connect_subject() in a subclass'

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
        if super(RelationshipConnect, self).connect(handle, port):
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
            old = line.subject
             
            connections = self.disconnect_connected_items()
            
            self.disconnect_subject(handle)
            if old:
                self.connect_connected_items(connections)

        super(RelationshipConnect, self).disconnect(handle)


# vim:sw=4:et:ai
