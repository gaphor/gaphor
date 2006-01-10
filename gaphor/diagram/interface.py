'''
InterfaceItem diagram item
'''
# vim:sw=4:et

from __future__ import generators

import math
import itertools
import gobject
import pango
import diacanvas
from gaphor import UML
from gaphor.diagram import initialize_item
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.implementation import ImplementationItem
from gaphor.diagram.interfaceicon import AssembledInterfaceIcon, \
    ProvidedInterfaceIcon, RequiredInterfaceIcon
from gaphor.diagram.rotatable import SimpleRotation
from nameditem import NamedItem
from klass import ClassItem
from relationship import RelationshipItem
from gaphor.misc.meta import GObjectPropsMerge


class InterfaceItem(ClassItem, SimpleRotation):
    """This item represents an interface drawn as a dot. The class-like
    representation is provided by ClassItem. These representations can be
    switched by using the Fold and Unfold actions.

    TODO (see also DependencyItem): when a Usage dependency is connected to
          the interface, draw a line, but not all the way to the connecting
          handle. Stop drawing the line 'x' points earlier. 
    """

    __metaclass__ = GObjectPropsMerge # merge properties from SimpleRotation

    def __init__(self, id=None):
        ClassItem.__init__(self, id)
        SimpleRotation.__init__(self, id)

        self._ricon = RequiredInterfaceIcon(self)
        self._aicon = AssembledInterfaceIcon(self)
        self._picon = ProvidedInterfaceIcon(self)

        self._icon = self._aicon


    def do_set_property(self, pspec, value):
        if pspec.name in SimpleRotation.__gproperties__:
            SimpleRotation.do_set_property(self, pspec, value)
        else:
            ClassItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name in SimpleRotation.__gproperties__:
            return SimpleRotation.do_get_property(self, pspec)
        else:
            return ClassItem.do_get_property(self, pspec)


    def set_drawing_style(self, style):
        """In addition to setting the drawing style, the handles are
        make non-movable if the icon (folded) style is used.
        """
        ClassItem.set_drawing_style(self, style)
        # TODO: adjust offsets so the center point is the same
        if self.drawing_style == self.DRAW_ICON:
            self.set(width = self._icon.width, height = self._icon.height)
            # Do not allow resizing of the node
            for h in self.handles:
                h.props.movable = False
        else:
            # Do allow resizing of the node
            for h in self.handles:
                h.props.movable = True


    def get_popup_menu(self):
        if self.drawing_style == self.DRAW_ICON:
            return NamedItem.popup_menu + ('separator', 'Rotate', 'Unfold',)
        else:
            return ClassItem.get_popup_menu(self)


    def is_folded(self):
        return self.drawing_style == self.DRAW_ICON


    def update_stereotype(self):
        if not ClassItem.update_stereotype(self):
            self.set_stereotype('interface')

 
    def update_icon(self, affine):
        # Figure out if this interface represents a required, provided,
        # assembled (wired) or dotted (minimal) look.
        usages = 0
        implementations = 0
        for h in self.connected_handles:
            ci = h.owner
            if gives_required(ci): 
                usages += 1
            elif gives_provided(ci):
                implementations += 1

        if usages > 0 and implementations == 0:
            self._icon = self._ricon
        elif usages > 0 and implementations > 0:
            self._icon = self._aicon
        else:
            self._picon.show_bar = implementations > 0
            self._icon = self._picon

        self._icon.update_icon()


    def on_update(self, affine):
        ClassItem.on_update(self, affine)

        #
        # do not put code below to update_icon method
        # class item on_update method must be run first
        #

        # update connected handles
        if self.is_folded():
            width = self._icon.width
            height = self._icon.height

            for h in self.connected_handles:
                if gives_provided(h.owner):
                    x, y = self._icon.get_provided_pos_w()
                    h.set_pos_w(x, y)
                    self.request_update()
                elif gives_required(h.owner):
                    x, y = self._icon.get_required_pos_w()
                    h.set_pos_w(x, y)
                    self.request_update()

            # center interface name
            name_width, name_height = self.get_name_size()
            xn = (width - name_width) / 2
            yn = height

            self.update_name(x = xn, y = yn, width = name_width, height = name_height)

            # set bounds
            x1, y1, x2, y2 = self.bounds
            if name_width > width: # expand bounds if name width is > than icon width
                x1 = xn
                x2 = xn + name_width
            y2 = yn + name_height # bottom is sum of icon height and name height

            self.set_bounds((x1, y1, x2, y2))


    def on_shape_iter(self):
        it = ClassItem.on_shape_iter(self)
        if self.drawing_style == self.DRAW_ICON:
            return itertools.chain(self._icon.on_shape_iter(), it)
        else:
            return it


    def on_connect_handle(self, handle):
        self.request_update()
        return ClassItem.on_connect_handle(self, handle)


    def on_disconnect_handle(self, handle):
        self.request_update()
        return ClassItem.on_disconnect_handle(self, handle)

    def rotate(self, step = 1):
        SimpleRotation.rotate(self, step)
        self.request_update()



def gives_provided(item):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be provided.
    """
    return isinstance(item, ImplementationItem)


def gives_required(item):
    """
    Check if an item connected to an interface changes semantics of this
    interface to be required.
    """
    return isinstance(item, DependencyItem) \
        and item.dependency_type is UML.Usage


initialize_item(InterfaceItem, UML.Interface)
