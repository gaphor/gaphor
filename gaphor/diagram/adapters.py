"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from interfaces import IConnect, IEditor
from elementitem import ElementItem
from nameditem import NamedItem
from comment import CommentItem
from commentline import CommentLineItem


class CommentItemEditor(object):
    """Text edit support for Comment item.
    """
    interface.implements(IEditor)
    component.adapts(CommentItem)

    def __init__(self, item):
	self._item = item

    def is_editable(self, x, y):
	return True

    def get_text(self):
	return self._item.subject.body

    def get_bounds(self):
	return None

    def update_text(self, text):
	self._item.subject.body = text

    def key_pressed(self, pos, key):
	pass

component.provideAdapter(CommentItemEditor)


class NamedItemEditor(object):
    """Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(NamedItem)

    def __init__(self, item):
	self._item = item

    def is_editable(self, x, y):
	return True

    def get_text(self):
	return self._item.subject.name

    def get_bounds(self):
	return None

    def update_text(self, text):
	self._item.subject.name = text

    def key_pressed(self, pos, key):
	pass

component.provideAdapter(NamedItemEditor)


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
            adapter = component.queryMultiAdapter((handle.connected_to, self.line), IConnect)
            adapter.disconnect(handle)
 
        # Stop here if no new connection should be established
        if not pos:
            return False

        s = self.side(pos, element)
        handle._connect_constraint = \
            constraint.LineConstraint(canvas, element, element.handles()[s],
                                element.handles()[(s+1)%4], self.line, handle)
        solver.add_constraint(handle._connect_constraint)
        handle.connected_to = element
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


# vim:sw=4:et:ai
