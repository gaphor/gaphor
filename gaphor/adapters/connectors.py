"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, NE, SW, SE
from gaphas.canvas import CanvasProjection
from gaphas.matrix import Matrix
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.interfaces import IConnect
from gaphor.diagram import items
from gaphor.misc.ipair import ipair

class AbstractConnect(object):
    """
    Connection adapter for Gaphor diagram items.

    Line item ``line`` connects with a handle to a connectable item ``element``.

    Line constraint is created between ``line`` handle and two handles of ``element``
    (called segment, see ``AbstractConnect._get_segment`` method).

    Attributes:

    - line: connecting item
    - element: connectable item
    - _canvas: canvas reference
    - _matrix_e2l: element to line matrix
    - _matrix_l2e: line to element matrix
    """
    interface.implements(IConnect)

    def __init__(self, element, line):
        self.element = element
        self.line = line
        canvas = self._canvas = element.canvas

        i2c = canvas.get_matrix_i2c
        c2i = canvas.get_matrix_c2i
        self._matrix_e2l = i2c(element) * c2i(line)
        self._matrix_l2e = i2c(line) * c2i(element)

        # code below returns None from transform_point... why?
        # self._matrix_l2e = Matrix(*self._matrix_e2l)
        # self._matrix_l2e.invert()


    def glue(self, handle):
        """
        Return the point the handle could connect to. None if no connection
        is allowed.
        """
        raise NotImplemented, 'Implement glue() in the subclass'

    def connect(self, handle):
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

        # Disconnect old model connection
        if handle.connected_to and handle.connected_to is not self.element:
            handle.disconnect()
 
        # Save guard: only connect if it's permitted by glue()
        #   -> glue() does not return None
        if not self.glue(handle):
            return False

        self.connect_constraints(handle)

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


    def connect_constraints(self, handle):
        """
        Create the actual constraint. The handle should be moved into connection
        position before this method is called.
        """
        h1, h2 = self._get_segment(handle)

        element = self.element
        line = self.line

        lc = constraint.LineConstraint(line=(CanvasProjection(h1.pos, element),
                                             CanvasProjection(h2.pos, element)),
                                       point=CanvasProjection(handle.pos, line))
        handle._connect_constraint = lc
        element.canvas.solver.add_constraint(lc)

        handle.connected_to = element


    def disconnect_constraints(self, handle):
        """
        Disconnect() takes care of disconnecting the handle from the
        element it's attached to, by removing the constraints.
        """
        try:
            self.line.canvas.solver.remove_constraint(handle._connect_constraint)
        except AttributeError:
            pass # No _connect_constraint property yet
        handle._connect_constraint = None


    def _get_segment(self, handle):
        """
        Get line segment, to which handle should connect to. Line segment is defined by two handles.
        Examples of line segmets
        - side of element item like class, action, etc.
        - line segment of association
        - lifeline's lifetime
        """
        raise NotImplemented()



class ElementConnect(AbstractConnect):
    """
    Base class for connecting a line to an ElementItem class.
    """

    def _get_segment(self, handle):
        """
        Determine the side on which the handle is connecting.
        This is done by determining the proximity to the nearest edge.

        Handles of one of the sides is returned.
        """
        handles = self.element.handles()
        l2e = self._matrix_l2e
        hx, hy = l2e.transform_point(*handle.pos)
        ax, ay = handles[NW].x, handles[NW].y
        bx, by = handles[SE].x, handles[SE].y

        if abs(hx - ax) < 0.01:
            return handles[NW], handles[SW]
        elif abs(hy - ay) < 0.01:
            return handles[NW], handles[NE]
        elif abs(hx - bx) < 0.01:
            return handles[NE], handles[SE]
        else:
            return handles[SW], handles[SE]
        assert False


    def bounds(self, element):
        """
        Returns bounds of the element that we're connecting to.
        """
        h = element.handles()
        return map(float, (h[NW].pos + h[SE].pos))


    def glue(self, handle):
        """
        Return the point the handle could connect to. None if no connection
        is allowed.
        """
        l2e = self._matrix_l2e
        e2l = self._matrix_e2l

        pos = l2e.transform_point(*handle.pos)
        bounds = self.bounds(self.element)

        pos = geometry.point_on_rectangle(bounds, pos, border=True)
        pos = e2l.transform_point(*pos)
        return pos



class LineConnect(AbstractConnect):
    """
    Base class for connecting two lines to each other.
    The line that is conencted to is called 'element', as in ElementConnect.

    Once a line has been connected at both ends, and a model element is
    assigned to it, all items connectedt to this line (e.g. Comments)
    receive a connect() call. This allows already connected lines to set
    up relationships at model level too.
    """

    def _get_segment_data(self, handle):
        """
        Get segment data
        - pos: position on a segment
        - h1: handle starting segment
        - h2: handle ending segment
        """
        dlp = geometry.distance_line_point

        handles = self.element.handles()

        def segment(h1, h2, pos):
            d, pos = dlp(h1.pos, h2.pos, pos)
            return d, pos, h1, h2

        pos = self._matrix_l2e.transform_point(*handle.pos)

        # find the nearest segment from handle
        data = (segment(h1, h2, pos) for h1, h2 in ipair(handles))
        # No key needed, distance is first
        d, pos, h1, h2 = min(data) #, key=lambda s: s[0])
        return pos, h1, h2


    def _get_segment(self, handle):
        """
        Return diagram line segment closest to a handle.
        """
        _, h1, h2 = self._get_segment_data(handle)
        return h1, h2


    def glue(self, handle):
        """
        Return a point on a connectable element closest to a handle.
        """
        pos, _, _ = self._get_segment_data(handle)
        return self._matrix_e2l.transform_point(*pos)



class CommentLineElementConnect(ElementConnect):
    """
    Connect a comment line to any element item.
    """
    component.adapts(items.ElementItem, items.CommentLineItem)

    def glue(self, handle):
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
        cls = items.CommentItem, items.CommentLineItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineElementConnect, self).glue(handle)

    def connect(self, handle):
        if super(CommentLineElementConnect, self).connect(handle):
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
    Connect a comment line to any diagram line.
    """
    component.adapts(items.DiagramLine, items.CommentLineItem)

    def glue(self, handle):
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
        cls = items.CommentItem, items.CommentLineItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super(CommentLineLineConnect, self).glue(handle)

    def connect(self, handle):
        if super(CommentLineLineConnect, self).connect(handle):
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
            elif opposite.connected_to.subject:
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
            relation = self.element_factory.create(type)
            setattr(relation, head[0], line.head.connected_to.subject)
            setattr(relation, tail[0], line.tail.connected_to.subject)
        return relation

    def connect_connected_items(self, connected_items=None):
        """
        Cause items connected to ``line`` to reconnect, allowing them to
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
            adapter.connect(handle)
        
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

    def connect(self, handle):
        """
        Connect the items to each other. The model level relationship
        is created by create_subject()
        """
        if super(RelationshipConnect, self).connect(handle):
            opposite = self.line.opposite(handle)
            if opposite.connected_to:
                self.connect_subject(handle)
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

    def glue(self, handle):
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

        return super(DependencyConnect, self).glue(handle)

    def connect_subject(self, handle):
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

    def glue(self, handle):
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

        return super(ImplementationConnect, self).glue(handle)

    def connect_subject(self, handle):
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
    def glue(self, handle):
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

        return super(GeneralizationConnect, self).glue(handle)

    def connect_subject(self, handle):
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

    def glue(self, handle):
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

        return super(IncludeConnect, self).glue(handle)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Include,
                    ('addition', None),
                    ('includingCase', 'include'))
        self.line.subject = relation

component.provideAdapter(IncludeConnect)


class ExtendConnect(RelationshipConnect):
    """
    Connect Usecases with a Extend relationship.
    """
    component.adapts(items.UseCaseItem, items.ExtendItem)

    def glue(self, handle):
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

        return super(ExtendConnect, self).glue(handle)

    def connect_subject(self, handle):
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

    def glue(self, handle):
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

        return super(ExtensionConnect, self).glue(handle)

    def connect_subject(self, handle):
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
             
            # TODO: make element at head end update!
            c1.request_update()

            # Find all associations and determine if the properties on
            # the association ends have a type that points to the class.
            for assoc in self.element_factory.select():
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
                            return
            else:
                # Create a new Extension relationship
                relation = self.element_factory.create(UML.Extension)
                head_end = self.element_factory.create(UML.Property)
                tail_end = self.element_factory.create(UML.ExtensionEnd)
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

    def glue(self, handle):
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

        return super(AssociationConnect, self).glue(handle)

    def connect_subject(self, handle):
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
            for assoc in self.element_factory.select():
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
                relation = self.element_factory.create(UML.Association)
                head_end = self.element_factory.create(UML.Property)
                head_end.lowerValue = self.element_factory.create(UML.LiteralSpecification)
                tail_end = self.element_factory.create(UML.Property)
                tail_end.lowerValue = self.element_factory.create(UML.LiteralSpecification)
                relation.package = element.canvas.diagram.namespace
                relation.memberEnd = head_end
                relation.memberEnd = tail_end
                head_end.type = head_type
                tail_end.type = tail_type
                head_type.ownedAttribute = tail_end
                tail_type.ownedAttribute = head_end

                line.head_end.subject = head_end
                line.tail_end.subject = tail_end
                # Do subject itself last, so event handlers can trigger
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
            del self.line.head_end.subject
            del self.line.tail_end.subject
            if old and len(old.presentation) == 0:
                for e in list(old.memberEnd):
                    e.unlink()
                old.unlink()


component.provideAdapter(AssociationConnect)


class FlowConnect(RelationshipConnect):
    """
    Connect FlowItem and Action/ObjectNode, initial/final nodes.
    """

    def glue(self, handle):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        subject = element.subject
        connected_to = opposite.connected_to

        if handle is line.head and isinstance(subject, UML.FinalNode) \
           or handle is line.tail and isinstance(subject, UML.InitialNode):
            return None

        return super(FlowConnect, self).glue(handle)

    def connect_subject(self, handle):
        line = self.line
        element = self.element
        # TODO: connect opposite side again (in case it's a join/fork or
        #       decision/merge node)
        if isinstance(line.head.connected_to, items.ObjectNodeItem) \
           or isinstance(line.tail.connected_to, items.ObjectNodeItem):
            relation = self.relationship_or_new(UML.ObjectFlow,
                        ('source', 'outgoing'),
                        ('target', 'incoming'))
        else:
            relation = self.relationship_or_new(UML.ControlFlow,
                        ('source', 'outgoing'),
                        ('target', 'incoming'))
        if not relation.guard:
            relation.guard = self.element_factory.create(UML.LiteralSpecification)
        line.subject = relation
        opposite = line.opposite(handle)
        if opposite and isinstance(opposite.connected_to, (items.ForkNodeItem, items.DecisionNodeItem)):
            adapter = component.queryMultiAdapter((opposite.connected_to, line), IConnect)
            adapter.combine_nodes()

    def disconnect_subject(self, handle):
        super(FlowConnect, self).disconnect_subject(handle)
        line = self.line
        opposite = line.opposite(handle)
        if opposite and isinstance(opposite.connected_to, (items.ForkNodeItem, items.DecisionNodeItem)):
            adapter = component.queryMultiAdapter((opposite.connected_to, line), IConnect)
            adapter.decombine_nodes()

component.provideAdapter(factory=FlowConnect,
                         adapts=(items.ActionItem, items.FlowItem))
component.provideAdapter(factory=FlowConnect,
                         adapts=(items.ActivityNodeItem, items.FlowItem))
component.provideAdapter(factory=FlowConnect,
                         adapts=(items.ObjectNodeItem, items.FlowItem))


class FlowForkDecisionNodeConnect(FlowConnect):
    """
    Abstract class with common behaviour for Fork/Join node and
    Decision/Merge node.
    """
    def glue(self, handle):
        """
        In addition to the normal check, one end should have at most one
        edge (incoming or outgoing).
        """
        opposite = self.line.opposite(handle)
        line = self.line
        element = self.element
        subject = element.subject
        connected_to = opposite.connected_to

        # Element can not connect back to itself
        if connected_to is element:
            return None

        # Same goes for subjects:
        if connected_to and \
                (not (connected_to.subject or element.subject)) \
                 and connected_to.subject is element.subject:
            return None

        # If one side of self.element has more than one edge, the
        # type of node is determined (either join or fork).
        #
        # TODO: remove these restrictions and create a combined join/fork or
        #       decision/merge node 
        #if handle is line.head and len(subject.incoming) > 1 and len(subject.outgoing) > 0:
        #    return None
        #
        #if handle is line.tail and len(subject.incoming) > 0 and len(subject.outgoing) > 1:
        #    return None

#        assert len(self.element.handles()) == 2, '%s: %d' % (self.element, len(self.element.handles()))
#        h1, h2 = self.element.handles()
#        return geometry.distance_line_point(h1.pos, h2.pos, (x, y))[1]

        return super(FlowForkDecisionNodeConnect, self).glue(handle)

    def combine_nodes(self):
        """
        Combine join/fork or decision/methe nodes into one diagram item.
        """
        fork_node_class = self.fork_node_class
        join_node_class = self.join_node_class
        line = self.line
        element = self.element
        subject = element.subject
        if len(subject.incoming) > 1 and len(subject.outgoing) < 2:
            self.element_factory.swap_element(subject, join_node_class)
            element.request_update()
        elif len(subject.incoming) < 2 and len(subject.outgoing) > 1:
            self.element_factory.swap_element(subject, fork_node_class)
            element.request_update()
        elif not element.combined and len(subject.incoming) > 1 and len(subject.outgoing) > 1:
            join_node = subject

            # determine flow class:
            if [ f for f in join_node.incoming if isinstance(f, UML.ObjectFlow) ]:
                flow_class = UML.ObjectFlow
            else:
                flow_class = UML.ControlFlow
            
            self.element_factory.swap_element(join_node, join_node_class)
            fork_node = self.element_factory.create(fork_node_class)
            for flow in list(join_node.outgoing):
                flow.source = fork_node
            flow = self.element_factory.create(flow_class)
            flow.source = join_node
            flow.target = fork_node

            element.combined = fork_node

    def decombine_nodes(self):
        """
        Decombine join/fork or decision/merge nodes.
        """
        fork_node_class = self.fork_node_class
        join_node_class = self.join_node_class
        line = self.line
        element = self.element
        if element.combined:
            join_node = element.subject
            flow = join_node.outgoing[0]
            fork_node = flow.target
            assert fork_node is element.combined
            assert isinstance(join_node, join_node_class)
            assert isinstance(fork_node, fork_node_class)

            if len(join_node.incoming) < 2 or len(fork_node.outgoing) < 2:
                # Move all outgoing edges to the first node (the join node):
                for flow in list(fork_node.outgoing):
                    flow.source = join_node
                flow.unlink()
                fork_node.unlink()

                # swap subject to fork node if outgoing > 1
                if len(join_node.outgoing) > 1:
                    assert len(join_node.incoming) < 2
                    self.element_factory.swap_element(join_node, fork_node_class)
                element.combined = None

    def connect_subject(self, handle):
        """
        In addition to a subject connect, the subject of the element may 
        be changed.
        For readability, parameters are named afther the classes used by
        Join/Fork nodes.
        """
        super(FlowForkDecisionNodeConnect, self).connect_subject(handle)

        # Switch class for self.element Join/Fork depending on the number
        # of incoming/outgoing edges.
        self.combine_nodes()

    def disconnect_subject(self, handle):
        super(FlowForkDecisionNodeConnect, self).disconnect_subject(handle)
        if self.element.combined:
            self.decombine_nodes()


class FlowForkNodeConnect(FlowForkDecisionNodeConnect):
    """
    Connect Flow to a ForkNode.
    """
    component.adapts(items.ForkNodeItem, items.FlowItem)

    fork_node_class=UML.ForkNode
    join_node_class=UML.JoinNode

    def _get_segment(self, handle):
        return self.element.handles()

    def bounds(self, element):
        h1, h2 = element.handles()
        return map(float, (h1.pos + h2.pos))

component.provideAdapter(FlowForkNodeConnect)


class FlowDecisionNodeConnect(FlowForkDecisionNodeConnect):
    """
    Connect Flow to a DecisionNode
    """
    component.adapts(items.DecisionNodeItem, items.FlowItem)

    fork_node_class = UML.DecisionNode
    join_node_class = UML.MergeNode

component.provideAdapter(FlowDecisionNodeConnect)


class MessageLifelineConnect(ElementConnect):
    """
    Connect lifeline with a message.
    """

    component.adapts(items.LifelineItem, items.MessageItem)

    element_factory = inject('element_factory')

    def connect_lifelines(self, line, send, received):
        """
        Always create a new Message with two EventOccurence instances.
        """
        def get_subject(c):
            if not line.subject:
                message = self.element_factory.create(UML.Message)
                line.subject = message
            return line.subject

        if send:
            message = get_subject(send)
            if not message.sendEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.sendMessage = message
                event.covered = send.subject

        if received:
            message = get_subject(received)
            if not message.receiveEvent:
                event = self.element_factory.create(UML.EventOccurrence)
                event.receiveMessage = message
                event.covered = received.subject

        if send and received:
            assert send.__class__ == received.__class__
            kind = 'complete'
        elif send and not received:
            kind = 'lost'
        elif not send and received:
            kind = 'found'

        message.messageKind = kind

    def disconnect_lifelines(self, line, send, received):
        """
        Disconnect lifeline and set appropriate kind of message item. If
        there are no lifelines connected on both ends, then set UML object
        (subject) to None.
        """
        if send:
            line.subject.messageKind = 'lost'
            event = line.subject.receiveEvent
            if event:
                event.receiveMessage = None
                event.covered = None
                del event

        if received:
            line.subject.messageKind = 'found'
            event = line.subject.sendEvent
            if event:
                event.sendMessage = None
                event.covered = None
                del event

        if not send and not received:
            line.subject = None

        if __debug__:
            m = line.subject

            # see semantics of message in UML specs
            assert not m or m and \
                (m.sendEvent and m.receiveEvent and m.messageKind == 'complete' \
                 or m.sendEvent and not m.receiveEvent and m.messageKind == 'lost' \
                 or not m.sendEvent and m.receiveEvent and m.messageKind == 'found')


    def _glue_lifetime(self, handle):
        """
        Glue ``handle`` to lifeline's lifetime.
        """
        lifetime = self.element.lifetime
        top = lifetime.top.pos
        bottom = lifetime.bottom.pos

        pos = self._matrix_l2e.transform_point(*handle.pos)
        d, pos = geometry.distance_line_point(top, bottom, pos)

        return self._matrix_e2l.transform_point(*pos)


    def glue(self, handle):
        """
        Glue to lifeline's head or lifetime. If lifeline's lifetime is
        visible then disallow connection to lifeline's head.
        """
        element = self.element
        lifetime = element.lifetime
        line = self.line
        opposite = line.opposite(handle)

        pos = None
        if lifetime.is_visible():
            if opposite.connected_to:
                glue_ok = opposite.connected_to.lifetime.is_visible()
            else:
                glue_ok = True

            # lifeline's lifetime is visible, therefore glue only when
            # opposite lifeline's lifetime is visible, too
            if glue_ok:
                pos = self._glue_lifetime(handle)
        else:
            pos = ElementConnect.glue(self, handle)
        return pos
        

    def _get_segment(self, handle):
        """
        Return handles of one of lifeline head's side or lifetime handles.
        """
        element = self.element
        if element.lifetime.is_visible():
            return element.handles()[-2:] # return lifeline's lifetime handles
        else:
            return super(MessageLifelineConnect, self)._get_segment(handle)
        assert False


    def connect(self, handle):
        if not ElementConnect.connect(self, handle):
            return

        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to
        self.connect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        # if no lifetime then disallow making lifetime visible
        if not lifetime.is_visible():
            lifetime.bottom.movable = False
        # todo: move code above to LifetimeItem class
        lifetime._messages_count += 1


    def disconnect(self, handle):
        ElementConnect.disconnect(self, handle)

        line = self.line
        send = line.head.connected_to
        received = line.tail.connected_to
        self.disconnect_lifelines(line, send, received)

        lifetime = self.element.lifetime
        lifetime._messages_count -= 1
        # if lifetime is not visible  and there are no messages connected
        # then allow to make lifetime visible
        # todo: move code below to LifetimeItem class
        if not lifetime.is_visible() and lifetime._messages_count < 1:
            lifetime.bottom.movable = True


component.provideAdapter(MessageLifelineConnect)

# vim:sw=4:et:ai
