"""
Classes for grouping different elements.
"""

import itertools

import gobject
import diacanvas

class GroupBase(diacanvas.CanvasGroupable):
    """
    This class allows to group different diagram elememnts. It should be
    set as a base class of main diagram element. Main diagram element
    (parent) has children.

    Children are specified as dictionary. Keys represent attributes of
    parent and values of dictionary should be instances of these
    attributes.
    """
    def __init__(self, children):
        diacanvas.CanvasGroupable.__init__(self)
        self.children = children
        log.debug('creating groupable with children: %s' % self.children.keys())
        for name, kid in children.items():
            setattr(self, name, kid)
            kid.set_child_of(self)


    def get_children(self):
        """
        Return children of parent.
        """
        return (getattr(self, kid) for kid in self.children.keys())


    def on_update(self, affine):
        """
        Update all children and calculate bounds which should include
        parent and all kids.
        """
        for kid in self.get_children():
            self.update_child(kid, affine)

        bounds = [self.bounds] \
            + [ kid.get_bounds(kid.affine) for kid in self.get_children() ]
        b0, b1, b2, b3 = itertools.izip(*bounds)
        self.set_bounds((min(b0), min(b1), max(b2), max(b3)))


    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the name to be removed.'''
        return 1

    def on_groupable_iter(self):
        return self.get_children()


class Groupable(gobject.GObjectMeta):
    """
    Metaclass for groupable diagram item classes.
    """
    def __new__(cls, name, bases, data):
        c = gobject.GObjectMeta.__new__(cls, name, bases, data)
        gobject.type_register(c)
        diacanvas.set_groupable(c)
        return c
