"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram import items
from gaphor.misc.ipair import ipair

class AbstractConnect(object):
    """
    Connection code, used by both ElementConnect and LineConnect.
    """
    interface.implements(IConnect)

    def __init__(self, element, line):
        self.element = element
        self.line = line

    def glue(self, handle, x, y):
        """
        Return the point the handle could connect to. None if no connection
        is allowed.
        """
        raise NotImplemented, 'Implement glue() in the subclass'

    def connect(self, handle, x, y):
        """
        Connect to an element. Note that at this point the line may
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
            handle.disconnect()
 
        # Stop here if no new connection should be established
        if not pos:
            return False
        
        self.connect_constraint(handle, pos[0], pos[1])

        # Set disconnect handler in the adapter, so it will also wotk if
        # connections are created programmatically.
        def _disconnect():
            self.disconnect(handle)
            handle.disconnect = lambda: 0
        handle.disconnect = _disconnect

        return True

    def disconnect(self, handle):
        """
        Do a full disconnect, also disconnect at UML model level.
        Subclasses should disconnect model-level connections.
        """
        self.disconnect_constraints(handle)
        handle.connected_to = None

    def connect_constraint(self, handle, x, y):
        """
        Create the actual constraint. The handle should be positioned before
        this method is called.
        x, y is the position the handle should have on the line.
        """
        raise NotImplemented, 'Implement connect_constraint() in a subclass'

    def disconnect_constraints(self, handle):
        """
        Disconnect() takes care of disconnecting the handle from the
        element it's attached to, by removing the constraints.
        """
        solver = self.line.canvas.solver
        try:
            solver.remove_constraint(handle._connect_constraint)
        except AttributeError:
            pass # No _connect_constraint property yet
        handle._connect_constraint = None


class ElementConnect(AbstractConnect):
    """
    Base class for connecting a line to an ElementItem class.
    """
    
    def side(self, handle_pos, glued):
        """
        Determine the side on which the handle is connecting.
        This is done by determining the proximity to the nearest edge.
        """
        hx, hy = handle_pos
        ax, ay = glued.handles()[NW].pos
        bx, by = glued.handles()[SE].pos
        return min((abs(hy - ay), 0), (abs(hx - bx), 1),
                   (abs(hy - by), 2),  (abs(hx - ax), 3))[1]

    def glue(self, handle, x, y):
        """
        Return the point the handle could connect to. None if no connection
        is allowed.
        """
        h = self.element.handles()
        bounds = map(float, (h[NW].pos + h[SE].pos))
        return geometry.point_on_rectangle(bounds, (x, y), border=True)

    def connect_constraint(self, handle, x, y):
        """
        Create the actual constraint. The handle should be positioned before
        this method is called.
        """
        element = self.element
        canvas = element.canvas
        solver = canvas.solver

        s = self.side((x, y), element)
        handle._connect_constraint = \
            constraint.LineConstraint(canvas, element, element.handles()[s],
                                element.handles()[(s+1)%4], self.line, handle)
        solver.add_constraint(handle._connect_constraint)
        handle.connected_to = element


class LineConnect(AbstractConnect):
    """
    Base class for connecting two lines to each other.
    The line that is conencted to is called 'element', as in ElementConnect.

    Once a line has been connected at both ends, and a model element is
    assigned to it, all items connectedt to this line (e.g. Comments)
    receive a connect() call. This allows already connected lines to set
    up relationships at model level too.
    """

    def _glue(self, handle, x, y):
        """
        Return the segment and  point on the element (DiagramLine)
        closest to (x, y).
        """
        h = self.element.handles()
        pos = (x, y)
        min_d = None
        segment = -1
        min_p = None
        dlp = geometry.distance_line_point
        for s, (h0, h1) in enumerate(ipair(h)):
            d, p = dlp(h0.pos, h1.pos, pos)
            if not s or d < min_d:
                min_d = d
                segment = s
                min_p = p
        return s, min_p

    def glue(self, handle, x, y):
        """
        Return the point on the element (DiagramLine) closest to (x, y)
        """
        return self._glue(handle, x, y)[1]

    def connect_constraint(self, handle, x, y):
        """
        Create the actual constraint. The handle should be positioned before
        this method is called.
        """
        element = self.element
        canvas = element.canvas
        solver = canvas.solver

        s, pos = self._glue(handle, x, y)
        handle._connect_constraint = \
            constraint.LineConstraint(canvas, element, element.handles()[s],
                                element.handles()[s+1], self.line, handle)
        solver.add_constraint(handle._connect_constraint)
        handle.connected_to = element


class CommentLineElementConnect(ElementConnect):
    """
    Connect a comment line to a comment item.
    Connect Comment.annotatedElement to any element
    """
    component.adapts(items.ElementItem, items.CommentLineItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            #print 'Subjects none or match:', connected_to.subject, element.subject
            return None

        # One end should be connected to a CommentItem:
        if connected_to and \
                ((isinstance(connected_to, items.CommentItem) and isinstance(self.element, items.CommentItem)) or \
                 (not isinstance(connected_to, items.CommentItem) and not isinstance(self.element, items.CommentItem))):
            return None

        return super(CommentLineElementConnect, self).glue(handle, x, y)

    def connect(self, handle, x, y):
        if super(CommentLineElementConnect, self).connect(handle, x, y):
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
        super(CommentLineElementConnect, self).disconnect(handle)

component.provideAdapter(CommentLineElementConnect)


class CommentLineLineConnect(LineConnect):
    """
    Connect a comment line to a comment item.
    Connect Comment.annotatedElement to any element
    """
    component.adapts(items.DiagramLine, items.CommentLineItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = opposite.connected_to
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # One end should be connected to a CommentItem:
        if connected_to and \
                ((isinstance(connected_to, items.CommentItem) and isinstance(self.element, items.CommentItem)) or \
                 (not isinstance(connected_to, items.CommentItem) and not isinstance(self.element, items.CommentItem))):
            return None

        return super(CommentLineLineConnect, self).glue(handle, x, y)

    def connect(self, handle, x, y):
        if super(CommentLineLineConnect, self).connect(handle, x, y):
            opposite = self.line.opposite(handle)
            if opposite.connected_to and self.element.subject:
                if isinstance(opposite.connected_to.subject, UML.Comment):
                    opposite.connected_to.subject.annotatedElement = self.element.subject
                else:
                    self.element.subject.annotatedElement = opposite.connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            if isinstance(handle.connected_to.subject, UML.Comment):
                del handle.connected_to.subject.annotatedElement[opposite.connected_to.subject]
            else:
                del opposite.connected_to.subject.annotatedElement[handle.connected_to.subject]
        super(CommentLineLineConnect, self).disconnect(handle)

component.provideAdapter(CommentLineLineConnect)


class RelationshipConnect(ElementConnect):
    """
    Base class for relationship connections, such as associations,
    dependencies and implementations.

    This class introduces a new method: relationship() which is used to
    find an existing relationship in the model that does not yet exist
    on the canvas.
    """

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

        head_subject = line.head.connected_to.subject
        tail_subject = line.tail.connected_to.subject

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
            relation = UML.create(type)
            setattr(relation, head[0], line.head.connected_to.subject)
            setattr(relation, tail[0], line.tail.connected_to.subject)
        return relation

    def connect_connected_items(self, connected_items=None):
        """
        Cause items connected to @line to reconnect, allowing them to
        establish or destroy relationships at model level.
        """
        line = self.line
        canvas = line.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        for item, handle in connected_items or line.canvas.get_connected_items(line):
            adapter = component.queryMultiAdapter((line, item), IConnect)
            assert adapter
            adapter.connect(handle, handle.x, handle.y)
        
    def disconnect_connected_items(self):
        """
        Cause items connected to @line to be disconnected.
        This is nessesary if the subject of the @line is to be removed.

        Returns a list of (item, handle) pairs that were connected (this
        list can be used to connect items again with connect_connected_items()).
        """
        line = self.line
        canvas = line.canvas
        solver = canvas.solver

        # First make sure coordinates match
        solver.solve()
        connected_items = list(line.canvas.get_connected_items(line))
        for item, handle in connected_items:
            adapter = component.queryMultiAdapter((line, item), IConnect)
            assert adapter
            adapter.disconnect(handle)
        return connected_items

    def connect_subject(self):
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

    def connect(self, handle, x, y):
        """
        Connect the items to each other. The model level relationship
        is created by create_subject()
        """
        if super(RelationshipConnect, self).connect(handle, x, y):
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                self.connect_subject()
                line = self.line
                if line.subject:
                    self.connect_connected_items()

    def disconnect(self, handle):
        """
        Disconnect model element.
        """
        line = self.line
        opposite = line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = line.subject
             
            connected_items = self.disconnect_connected_items()
            
            self.disconnect_subject(handle)
            if old:
                self.connect_connected_items(connected_items)

        super(RelationshipConnect, self).disconnect(handle)


class DependencyConnect(RelationshipConnect):
    """
    Connect two NamedItem elements using a Dependency
    """
    component.adapts(items.NamedItem, items.DependencyItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # Element should be a NamedElement
        if not element.subject or \
           not isinstance(element.subject, UML.NamedElement):
            return None

        return super(DependencyConnect, self).glue(handle, x, y)

    def connect_subject(self):
        """
        TODO: cleck for existing relationships (use self.relation())
        """
        line = self.line
        if line.auto_dependency:
            line.set_dependency_type()
        if line.dependency_type is UML.Realization:
            relation = self.relationship_or_new(line.dependency_type,
                                head=('realizingClassifier', None),
                                tail=('abstraction', 'realization'))
        else:
            relation = self.relationship_or_new(line.dependency_type,
                                ('supplier', 'supplierDependency'),
                                ('client', 'clientDependency'))
        line.subject = relation

component.provideAdapter(DependencyConnect)


class ImplementationConnect(RelationshipConnect):
    """
    Connect Interface and a BehavioredClassifier using an Implementation
    """
    component.adapts(items.NamedItem, items.ImplementationItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # Element at the head should be an Interface
        if handle is line.head and \
           not isinstance(element.subject, UML.Interface):
            return None

        # Element at the tail should be a BehavioredClassifier
        if handle is line.tail and \
           not isinstance(element.subject, UML.BehavioredClassifier):
            return None

        return super(ImplementationConnect, self).glue(handle, x, y)

    def connect_subject(self):
        relation = self.relationship_or_new(UML.Implementation,
                    ('contract', None),
                    ('implementatingClassifier', 'implementation'))
        self.line.subject = relation

component.provideAdapter(ImplementationConnect)


class GeneralizationConnect(RelationshipConnect):
    """
    Connect Classifiers with a Generalization relationship.
    """
    component.adapts(items.ClassifierItem, items.GeneralizationItem)

#    # FixMe: Both ends of the generalization should be of the same  type?
    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        return super(GeneralizationConnect, self).glue(handle, x, y)

    def connect_subject(self):
        relation = self.relationship_or_new(UML.Generalization,
                    ('general', None),
                    ('specific', 'generalization'))
        self.line.subject = relation

component.provideAdapter(GeneralizationConnect)


class IncludeConnect(RelationshipConnect):
    """
    Connect Usecases with a Include relationship.
    """
    component.adapts(items.UseCaseItem, items.IncludeItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to
        
        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super(IncludeConnect, self).glue(handle, x, y)

    def connect_subject(self):
        relation = self.relationship_or_new(UML.Include,
                    ('addition', None),
                    ('includingCase', 'include'))
        line.subject = relation

component.provideAdapter(IncludeConnect)


class ExtendConnect(RelationshipConnect):
    """
    Connect Usecases with a Extend relationship.
    """
    component.adapts(items.UseCaseItem, items.ExtendItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to
        
        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        if not (element.subject and isinstance(element.subject, UML.UseCase)):
            return None

        return super(ExtendConnect, self).glue(handle, x, y)

    def connect_subject(self):
        relation = self.relationship_or_new(UML.Extend,
                    ('extendedCase', None),
                    ('extension', 'extend'))
        line.subject = relation

component.provideAdapter(ExtendConnect)


class ExtensionConnect(RelationshipConnect):
    """
    Connect Class and a Stereotype using an Extension
    """
    component.adapts(items.ClassifierItem, items.ExtensionItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element can not be a parent for itself.
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # Element at the head should be a Class
        if handle is line.head and \
           not isinstance(element.subject, UML.Class):
            return None

        # Element at the tail should be a Stereotype
        if handle is line.tail and \
           not isinstance(element.subject, UML.Stereotype):
            return None

        return super(ExtensionConnect, self).glue(handle, x, y)

    def connect_subject(self):
        element = self.element
        line = self.line

        c1 = line.head.connected_to
        c2 = line.tail.connected_to
        if c1 and c2:
            head_type = c1.subject
            tail_type = c2.subject

            # First check if we do not already contain the right subject:
            if line.subject:
                end1 = line.subject.memberEnd[0]
                end2 = line.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    return
                    
            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            for assoc in UML.select():
                if isinstance(assoc, UML.Extension):
                    end1 = assoc.memberEnd[0]
                    end2 = assoc.memberEnd[1]
                    if (end1.type is head_type and end2.type is tail_type) \
                       or (end2.type is head_type and end1.type is tail_type):
                        # check if this entry is not yet in the diagram
                        # Return if the association is not (yet) on the canvas
                        for item in assoc.presentation:
                            if item.canvas is element.canvas:
                                break
                        else:
                            line.subject = assoc
#                                    if (end1.type is head_type and end2.type is tail_type):
#                                        line.head_subject = end1
#                                        line.tail_subject = end2
#                                    else:
#                                        line.head_subject = end2
#                                        line.tail_subject = end1
                            return
            else:
                # Create a new Extension relationship
                relation = UML.create(UML.Extension)
                head_end = UML.create(UML.Property)
                tail_end = UML.create(UML.ExtensionEnd)
                relation.package = element.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                relation.ownedEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                tail_type.ownedAttribute = head_end
                head_end.name = 'baseClass'

        line.subject = relation

    def disconnect_subject(self, handle):
        """
        Disconnect model element.
        Disconnect property (memberEnd) too, in case of end of life for
        Extension
        """
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = self.line.subject
            del self.line.subject
            if old and len(old.presentation) == 0:
                for e in old.memberEnd:
                    e.unlink()
                old.unlink()


component.provideAdapter(ExtensionConnect)


class AssociationConnect(RelationshipConnect):
    """
    Connect Class and a Stereotype using an Extension
    """
    component.adapts(items.ClassifierItem, items.AssociationItem)

    def glue(self, handle, x, y):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        connected_to = opposite.connected_to

        # Element should be a Classifier
        if not isinstance(element.subject, UML.Classifier):
            return None

        return super(AssociationConnect, self).glue(handle, x, y)

    def connect_subject(self):
        element = self.element
        line = self.line

        c1 = line.head.connected_to
        c2 = line.tail.connected_to
        if c1 and c2:
            head_type = c1.subject
            tail_type = c2.subject

            # First check if we do not already contain the right subject:
            if line.subject:
                end1 = line.subject.memberEnd[0]
                end2 = line.subject.memberEnd[1]
                if (end1.type is head_type and end2.type is tail_type) \
                   or (end2.type is head_type and end1.type is tail_type):
                    return
                    
            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            for assoc in UML.select():
                if isinstance(assoc, UML.Association):
                    end1 = assoc.memberEnd[0]
                    end2 = assoc.memberEnd[1]
                    if (end1.type is head_type and end2.type is tail_type) \
                       or (end2.type is head_type and end1.type is tail_type):
                        # check if this entry is not yet in the diagram
                        # Return if the association is not (yet) on the canvas
                        for item in assoc.presentation:
                            if item.canvas is element.canvas:
                                break
                        else:
                            line.subject = assoc
                            if (end1.type is head_type and end2.type is tail_type):
                                line.head_end.subject = end1
                                line.tail_end.subject = end2
                            else:
                                line.head_end.subject = end2
                                line.tail_end.subject = end1
                            return
            else:
                # Create a new Extension relationship
                relation = UML.create(UML.Association)
                head_end = UML.create(UML.Property)
                head_end.lowerValue = UML.create(UML.LiteralSpecification)
                tail_end = UML.create(UML.Property)
                tail_end.lowerValue = UML.create(UML.LiteralSpecification)
                relation.package = element.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                head_type.ownedAttribute = tail_end
                tail_type.ownedAttribute = head_end

                line.subject = relation
                line.head_end.subject = head_end
                line.tail_end.subject = tail_end

    def disconnect_subject(self, handle):
        """
        Disconnect model element.
        Disconnect property (memberEnd) too, in case of end of life for
        Extension
        """
        opposite = self.line.opposite(handle)
        if handle.connected_to and opposite.connected_to:
            old = self.line.subject
            del self.line.subject
            del self.line.head_end.subject
            del self.line.tail_end.subject
            if old and len(old.presentation) == 0:
                for e in list(old.memberEnd):
                    e.unlink()
                old.unlink()


component.provideAdapter(AssociationConnect)


# vim:sw=4:et:ai
