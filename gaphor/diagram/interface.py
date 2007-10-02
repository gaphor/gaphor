"""
Interface item.
"""

import itertools
from math import pi
from gaphas.item import NW, SE, NE, SW
from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_TOP, ALIGN_BOTTOM, ALIGN_CENTER


class InterfaceItem(ClassItem):
    """
    This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be
    switched by using the Fold and Unfold actions.

    TODO (see also DependencyItem): when a Usage dependency is connected to
          the interface, draw a line, but not all the way to the connecting
          handle. Stop drawing the line 'x' points earlier. 
    """

    __uml__        = UML.Interface
    __stereotype__ = {'interface': lambda self: self.drawing_style != self.DRAW_ICON}
    __style__ = {
        'icon-size': (20, 20),
        'icon-size-provided': (20, 20),
        'icon-size-required': (28, 28),
        'name-outside': False,
    }

    UNFOLDED_STYLE = {
        'text-align': (ALIGN_CENTER, ALIGN_TOP),
        'text-outside': False,
    }

    FOLDED_STYLE = {
        'text-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'text-outside': True,
    }

    RADIUS_PROVIDED = 10
    RADIUS_REQUIRED = 14

    def __init__(self, id=None):
        ClassItem.__init__(self, id)
        self._draw_required = False
        self._draw_provided = False

        self.add_watch(UML.Interface.ownedAttribute, self.on_class_owned_attribute)
        self.add_watch(UML.Interface.ownedOperation, self.on_class_owned_operation)

    @observed
    def set_drawing_style(self, style):
        """
        In addition to setting the drawing style, the handles are
        make non-movable if the icon (folded) style is used.
        """
        ClassItem.set_drawing_style(self, style)
        # TODO: adjust offsets so the center point is the same
        if self._drawing_style == self.DRAW_ICON:
            self._name.style.update(self.FOLDED_STYLE)
            for h in self._handles: h.movable = False
            self.request_update()
        else:
            self._name.style.update(self.UNFOLDED_STYLE)
            for h in self._handles: h.movable = True
            self.request_update()

    drawing_style = reversible_property(lambda self: self._drawing_style, set_drawing_style)

    def is_folded(self):
        """
        Returns True if the interface is drawn as a circle/dot.
        Unfolded means it's drawn like a classifier.
        """
        return self.drawing_style == self.DRAW_ICON

    def _set_folded(self, folded):
        if folded:
            self.drawing_style = self.DRAW_ICON
        else:
            self.drawing_style = self.DRAW_COMPARTMENT

    folded = property(is_folded, _set_folded)

    def pre_update_icon(self, context):
        """
        Figure out if this interface represents a required, provided,
        assembled (wired) or dotted (minimal) look.
        """

        self._draw_required = self._draw_provided = False
        for item, handle in self.canvas.get_connected_items(self):
            if gives_required(item, handle):
                self._draw_required = True
            elif gives_provided(item, handle):
                self._draw_provided = True
        radius = self.RADIUS_PROVIDED
        self.style.icon_size = self.style.icon_size_provided
        if self._draw_required:
            radius = self.RADIUS_REQUIRED
            self.style.icon_size = self.style.icon_size_required

        self.min_width, self.min_height = self.style.icon_size
        self.width, self.height = self.style.icon_size

        # change handles first so gaphas.Element.pre_update can
        # update its state
        #
        # update only h_se handle - rest of handles should be updated by
        # constraints
        h_nw = self._handles[NW]
        h_se = self._handles[SE]
        h_se.x = h_nw.x + self.min_width
        h_se.y = h_nw.y + self.min_height

        super(InterfaceItem, self).pre_update_icon(context)

    def draw_icon(self, context):
        cr = context.cairo
        h_nw = self._handles[NW]
        cx, cy = h_nw.x + self.width/2, h_nw.y + self.height/2
        if self._draw_required:
            cr.move_to(cx, cy + self.RADIUS_REQUIRED)
            cr.arc_negative(cx, cy, self.RADIUS_REQUIRED, pi/2, pi*1.5)
            cr.stroke()
        if self._draw_provided or not self._draw_required:
            cr.move_to(cx + self.RADIUS_PROVIDED, cy)
            cr.arc(cx, cy, self.RADIUS_PROVIDED, 0, pi*2)
            cr.stroke()
        super(InterfaceItem, self).draw(context)


def gives_provided(item, handle):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be provided.

    handle - handle of an item
    """
    return isinstance(item, ImplementationItem)


def gives_required(item, handle):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be required.

    handle - handle of an item
    TODO: check subject.clientDependency and subject.supplierDependency
    """
    # check for dependency item, interfaces is required if
    # - connecting handle is head one
    # - is in auto dependency
    # - if is not in auto dependency then its UML type is Usage
    return isinstance(item, DependencyItem) and item.handles()[0] == handle \
        and (not item.auto_dependency and item.dependency_type is UML.Usage
            or item.auto_dependency)


# vim:sw=4:et
