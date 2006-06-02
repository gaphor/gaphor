"""
Classes for grouping different elements.
"""

import itertools

import gobject
import diacanvas

# TODO: Remove alltogether (no longer used for Gaphas)
class GroupBase(diacanvas.CanvasGroupable):
    """
    This class allows to group different diagram elememnts. It should be
    set as a base class of main diagram element. Main diagram element
    (parent) has children.
    """
    def __init__(self):
        diacanvas.CanvasGroupable.__init__(self)
        self.children = set()


    def on_update(self, affine):
        """
        Update all children and calculate bounds which should include
        parent and all kids.
        """
        bounds = [self.bounds]
        for kid in self.children:
            self.update_child(kid, affine)
            bounds.append(kid.get_bounds(kid.affine))

        b0, b1, b2, b3 = itertools.izip(*bounds)
        self.set_bounds((min(b0), min(b1), max(b2), max(b3)))


    #
    # groupable interface
    #
    def on_groupable_add(self, item):
        self.children.add(item)
        item.set_child_of(self)
        return True


    def on_groupable_remove(self, item):
        self.children.remove(item)
        item.set_child_of(None)
        return True


    def on_groupable_iter(self):
        return iter(self.children)
