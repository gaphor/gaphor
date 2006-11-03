"""
Interface item.
"""

import itertools
from gaphas.item import NW, SE
from gaphor import UML
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem
#from gaphor.diagram.interfaceicon import AssembledInterfaceIcon, \
#    ProvidedInterfaceIcon, RequiredInterfaceIcon
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.rotatable import SimpleRotation

class InterfaceItem(ClassItem, SimpleRotation):
    """This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be
    switched by using the Fold and Unfold actions.

    TODO (see also DependencyItem): when a Usage dependency is connected to
          the interface, draw a line, but not all the way to the connecting
          handle. Stop drawing the line 'x' points earlier. 
    """

    __uml__        = UML.Interface
    __stereotype__ = {'interface': lambda self: self.drawing_style != self.DRAW_ICON}

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None):
        ClassItem.__init__(self, id)
        SimpleRotation.__init__(self)
        self._draw_required = False
        self._draw_provided = False

#        self._ricon = RequiredInterfaceIcon(self)
#        self._aicon = AssembledInterfaceIcon(self)
#        self._picon = ProvidedInterfaceIcon(self)
#
#        self._icon = self._aicon


#    def set_drawing_style(self, style):
#        """In addition to setting the drawing style, the handles are
#        make non-movable if the icon (folded) style is used.
#        """
#        ClassItem.set_drawing_style(self, style)
#        # TODO: adjust offsets so the center point is the same
#        if self.drawing_style == self.DRAW_ICON:
#            self.set(width = self._icon.width, height = self._icon.height)
#            # Do not allow resizing of the node
#            for h in self.handles:
#                h.props.movable = False
#
#            # copy align data from class to item instance, we need this because
#            # interface align data can change because of folding/unfolding
#            # interface
#            self.s_align = self.s_align.copy()
#            self.n_align = self.n_align.copy()
#
#            self.s_align.valign = V_ALIGN_BOTTOM
#            self.s_align.outside = True
#            self.s_align.margin = (0, 2) * 4
#            self.n_align.valign = V_ALIGN_BOTTOM
#            self.n_align.outside = True
#            self.n_align.margin = (2, ) * 4
#
#            self._shapes.remove(self._border)
#
#            # update connected handles
#            self.update_handle_pos()
#        else:
#            # Do allow resizing of the node
#            for h in self.handles:
#                h.props.movable = True
#
#            # back to default InterfaceItem class align
#            del self.s_align
#            del self.n_align
#
#            self._shapes.add(self._border)
#
#        self.update_stereotype()


#    def update_handle_pos(self):
#        """
#        Update connected lines position.
#        """
#        for h in self.connected_handles:
#            f = None
#            if gives_provided(h):
#                f = self._icon.get_provided_pos_w
#            elif gives_required(h):
#                f = self._icon.get_required_pos_w
#            if f:
#                x, y = f()
#                h.set_pos_w(x, y)
#                self.connect_handle(h)


#    def get_popup_menu(self):
#        if self.drawing_style == self.DRAW_ICON:
#            return NamedItem.popup_menu + ('separator', 'Rotate', 'Unfold',)
#        else:
#            return ClassItem.get_popup_menu(self)


    def is_folded(self):
        """Returns True if the interface is drawn as a circle/dot.
        Unfolded means it's drawn like a classifier.
        """
        return self.drawing_style == self.DRAW_ICON

 
    def update_icon(self, context):
        """Figure out if this interface represents a required, provided,
        assembled (wired) or dotted (minimal) look.
        """
        h_nw = self._handles[NW]
        cx, xy = h_nw.x + self.width/2, h_nw.y + self.height/2
        self._draw_required = self._draw_provided = False
        for item, handle in self.canvas.get_connected_items(self):
            if gives_required(handle):
                self._draw_required = True
            elif gives_provided(handle):
                self._draw_provided = True
        radius = RADIUS_PROVIDED
        if self._draw_required:
            radius = RADIUS_REQUIRED

        h_nw.x, h_nw.y = cx - radius, cy - radius
        h_se = self._handles[SE]
        h_se.x, h_se.y = cx + radius, cy + radius


    def draw_icon(self, context):
        cr = context.cairo
        h_nw = self._handles[NW]
        cx, cy = h_nw.x + self.width/2, h_nw.y + self.height/2
        if self._draw_required:
            cr.move_to(cx, cy + RADIUS_REQUIRED)
            cr.arc_negative(cx, cy, RADIUS_REQUIRED, pi/2, pi*1.5)
            cr.stroke()
        if self._draw_provided or not self._draw_required:
            cr.move_to(cx + RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, RADIUS_PROVIDED, 0, pi*2)
            cr.stroke()

    def on_glue(self, handle, wx, wy):
        """Allow connect only to provided/required points in case
        of interface icon.
        In folded mode, only allow connections from Implementation and
        Realization dependencies.
        """
        if self.drawing_style == self.DRAW_ICON:
            if d < 15:
                f = None
                if gives_provided(handle):
                    f = self._icon.get_provided_pos_w
                elif gives_required(handle):
                    f = self._icon.get_required_pos_w

                if f:
                    p2 = f()
                    p1 = p2
        return d, p1


    def rotate(self, step = 1):
        """
        Update connected handle positions after rotation.
        """
        SimpleRotation.rotate(self, step)
        self.update_handle_pos()



def gives_provided(handle):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be provided.

    handle - handle of an item
    """
    return isinstance(handle.owner, ImplementationItem)


def gives_required(handle):
    """Check if an item connected to an interface changes semantics of this
    interface to be required.

    handle - handle of an item
    TODO: check subject.clientDependency and subject.supplierDependency
    """
    item = handle.owner
    # check for dependency item, interfaces is required if
    # - connecting handle is head one
    # - is in auto dependency
    # - if is not in auto dependency then its UML type is Usage
    return isinstance(item, DependencyItem) and item.handles[0] == handle \
        and (not item.auto_dependency and item.dependency_type is UML.Usage
            or item.auto_dependency)


# vim:sw=4:et
