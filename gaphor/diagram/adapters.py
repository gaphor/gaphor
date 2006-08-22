"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from interfaces import IConnect, IEditor
from elementitem import ElementItem
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
        """
        print 'connect'
        element = self.element
        canvas = element.canvas
        solver = canvas.solver
        pos = self.glue(handle, x, y)

        # Disconnect old model connection
        print 'connect - disconnect'
        if handle.connected_to and handle.connected_to is not self.element:
            adapter = component.queryMultiAdapter((handle.connected_to, self.line), IConnect)
            adapter.full_disconnect(handle)
 
        # Stop here if no new connection should be established
        if not pos:
            return

        print 'connect - connect'

        s = self.side(pos, element)
        #try:
        #    solver.remove_constraint(handle._connect_constraint)
        #except AttributeError:
        #    pass # No _connect_constraint property yet
        handle._connect_constraint = \
            constraint.LineConstraint(canvas, element, element.handles()[s],
                                element.handles()[(s+1)%4], self.line, handle)
        solver.add_constraint(handle._connect_constraint)
        handle.connected_to = element

    def disconnect(self, handle):
        """Disconnect() takes care of disconnecting the handle from the
        element it's attached to, by removing the constraints.
        """
        print 'disconnect'
        solver = self.element.canvas.solver
        try:
            solver.remove_constraint(handle._connect_constraint)
        except AttributeError:
            pass # No _connect_constraint property yet
        handle._connect_constraint = None

    def full_disconnect(self, handle):
        """Do a full disconnect, also disconnect at UML model level.
        """
        handle.connected_to = None
        # TODO: disconnect at model level


class CommentLineToCommentConnect(SimpleConnect):
    """Connect a comment line to a comment item.
    """
    component.adapts(CommentItem, CommentLineItem)

component.provideAdapter(CommentLineToCommentConnect)


class CommentLineToElementConnect(SimpleConnect):
    """Connect a comment line to a generic element (not a comment item)
    """
    component.adapts(ElementItem, CommentLineItem)

component.provideAdapter(CommentLineToElementConnect)


# vim:sw=4:et:ai
