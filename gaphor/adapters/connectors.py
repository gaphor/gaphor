"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem


class SimpleConnect(object):
    interface.implements(IConnect)

    def __init__(self, element, line):
        self.element = element
        self.line = line

    def side(self, handle_pos, glued):
        """Determine the side on which the handle is connecting.
        This is done by determining the proximity to the nearest edge.
        """
        hx, hy = handle_pos
        ax, ay = glued.handles()[NW].pos
        bx, by = glued.handles()[SE].pos
        if abs(hx - ax) < 0.01:
            side = 3
        elif abs(hy - ay) < 0.01:
            side = 0
        elif abs(hx - bx) < 0.01:
            side = 1
        else:
            side = 2
        return side

    def glue(self, handle, x, y):
        """Return the point the handle could connect to. None if no connection
        is allowed.
        """
        h = self.element.handles()
        bounds = (h[NW].pos + h[SE].pos)
        return geometry.point_on_rectangle(bounds, (x, y), border=True)

    def connect(self, handle, x, y):
        """Connect to an element. Note that at this point the line may
        be connected to some other, or the same element by means of the
        handle.connected_to property. Also the connection at UML level
        still exists.
        
        Returns True if a connection is established.
        """
        element = self.element
        canvas = element.canvas
        solver = canvas.solver
        pos = self.glue(handle, x, y)

        # Disconnect old model connection
        if handle.connected_to and handle.connected_to is not self.element:
            #adapter = component.queryMultiAdapter((handle.connected_to, self.line), IConnect)
            #adapter.disconnect(handle)
            #print 'disconnect is', handle.disconnect
            handle.disconnect()
 
        # Stop here if no new connection should be established
        if not pos:
            return False

        s = self.side(pos, element)
        handle._connect_constraint = \
            constraint.LineConstraint(canvas, element, element.handles()[s],
                                element.handles()[(s+1)%4], self.line, handle)
        solver.add_constraint(handle._connect_constraint)
        handle.connected_to = element
        
        # Set disconnect handler in the adapter, so it will also wotk if
        # connections are created programmatically.
        def _disconnect():
            self.disconnect(handle)
            handle.disconnect = lambda: 0
        handle.disconnect = _disconnect

        return True

    def disconnect_constraints(self, handle):
        """Disconnect() takes care of disconnecting the handle from the
        element it's attached to, by removing the constraints.
        """
        solver = self.element.canvas.solver
        try:
            solver.remove_constraint(handle._connect_constraint)
        except AttributeError:
            pass # No _connect_constraint property yet
        handle._connect_constraint = None

    def disconnect(self, handle):
        """Do a full disconnect, also disconnect at UML model level.
        Subclasses should disconnect model-level connections.
        """
        self.disconnect_constraints(handle)
        handle.connected_to = None


class CommentLineConnect(SimpleConnect):
    """Connect a comment line to a comment item.
    Connect Comment.annotatedElement to any element
    """
    component.adapts(ElementItem, CommentLineItem)

    def glue(self, handle, x, y):
        """In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to
        if connected_to is element:
            #print 'item identical', connected_to, element
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            #print 'Subjects none or match:', connected_to.subject, element.subject
            return None

        # One end should be connected to a CommentItem:
        if connected_to and \
                ((isinstance(connected_to, CommentItem) and isinstance(self.element, CommentItem)) or \
                 (not isinstance(connected_to, CommentItem) and not isinstance(self.element, CommentItem))):
            return None

        return super(CommentLineConnect, self).glue(handle, x, y)

    def connect(self, handle, x, y):
        if super(CommentLineConnect, self).connect(handle, x, y):
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                if isinstance(opposite.connected_to.subject, UML.Comment):
                    opposite.connected_to.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = opposite.connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            if isinstance(opposite.connected_to.subject, UML.Comment):
                del opposite.connected_to.subject.annotatedElement[handle.connected_to.subject]
            else:
                del handle.connected_to.subject.annotatedElement[opposite.connected_to.subject]
        super(CommentLineConnect, self).disconnect(handle)

component.provideAdapter(CommentLineConnect)


class RelationshipConnect(SimpleConnect):
    """Base class for relationship connections, such as Association,
    dependencies and implementations.

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    The subclasses should define HEAD and TAIL as the relationship that
    should be established between head and tail of the connecting item.
    """

    def relationship(self, required_type, head, tail):
        """Figure out what elements are used in a relationship.
        type - the type of relationship we're looking for
        head - tuple (association name on line, association name on element)
        tail - tuple (association name on line, association name on element)
        """
        line = self.line

        head_subject = line.head.connected_to.subject
        tail_subject = line.tail.connected_to.subject

        edge_head_name = head[0] or self.HEAD[0]
        node_head_name = head[1] or self.HEAD[1]
        edge_tail_name = tail[0] or self.TAIL[0]
        node_tail_name = tail[1] or self.TAIL[1]

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
        """Like relation(), but create a new instance of none was found.
        """
        relation = self.relationship(type, head, tail)
        if not relation:
            line = self.line
            relation = UML.create(type)
            setattr(relation, head[0], line.head.connected_to.subject)
            setattr(relation, tail[0], line.tail.connected_to.subject)
        return relation

    def disconnect(self, handle):
        """Disconnect model element.
        """
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            self.line.set_subject(None)
        super(RelationshipConnect, self).disconnect(handle)


class DependencyConnect(RelationshipConnect):
    """Connect two NamedItem elements using a Dependency
    """
    component.adapts(NamedItem, DependencyItem)

    def glue(self, handle, x, y):
        """In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to

        # Element should be a NamedElement
        if not element.subject or \
           not isinstance(element.subject, UML.NamedElement):
            return None

        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        return super(DependencyConnect, self).glue(handle, x, y)

    def connect(self, handle, x, y):
        """
        TODO: cleck for existing relationships (use self.relation())
        """
        if super(DependencyConnect, self).connect(handle, x, y):
            dep = self.line
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                if dep.auto_dependency:
                    dep.set_dependency_type()
                if dep.dependency_type is UML.Realization:
                    relation = self.relationship_or_new(dep.dependency_type,
                                        head=('realizingClassifier', None),
                                        tail=('abstraction', 'realization'))
                else:
                    relation = self.relationship_or_new(dep.dependency_type,
                                        ('supplier', 'supplierDependency'),
                                        ('client', 'clientDependency'))
                dep.subject = relation

component.provideAdapter(DependencyConnect)


class ImplementationConnect(RelationshipConnect):
    """Connect Interface and a BehavioredClassifier using an Implementation
    """
    component.adapts(NamedItem, ImplementationItem)

    HEAD = 'contract', None
    TAIL = 'implementatingClassifier', 'implementation'

    def glue(self, handle, x, y):
        """In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element at the head should be an Interface
        if handle is line.head and \
           not isinstance(element.subject, UML.Interface):
            return None

        # Element at the tail should be a BehavioredClassifier
        if handle is line.tail and \
           not isinstance(element.subject, UML.BehavioredClassifier):
            return None

        return super(ImplementationConnect, self).glue(handle, x, y)

    def connect(self, handle, x, y):
        if super(ImplementationConnect, self).connect(handle, x, y):
            line = self.line
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                relation = self.relationship_or_new(UML.Implementation,
                            ('contract', None),
                            ('implementatingClassifier', 'implementation'))
                line.subject = relation

component.provideAdapter(ImplementationConnect)


# vim:sw=4:et:ai
