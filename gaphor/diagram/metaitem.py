#!/usr/bin/env python
#
# MetaItem
#
# Handle registration of GObject types.
#
# vim: sw=4

__version__ = '$Revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'

#from gobject import type_register
import gobject
import diacanvas
#from diacanvas import set_callbacks, set_groupable
#from diacanvas import CanvasItem, CanvasGroup, CanvasAbstractGroup, \
#                CanvasLine, CanvasElement, CanvasBox, CanvasText, CanvasImage

class MetaItem (type):
    def __new__ (self, name, bases, members):
        new_class = type.__new__ (self, name, bases, members)
        print 'MetaItem:', new_class
        gobject.type_register (new_class)
        if (diacanvas.CanvasItem in bases) or \
            (diacanvas.CanvasGroup in bases) or \
            (diacanvas.CanvasLine in bases) or \
            (diacanvas.CanvasElement in bases) or \
            (diacanvas.CanvasBox in bases) or \
            (diacanvas.CanvasText in bases) or \
            (diacanvas.CanvasImage in bases):
            diacanvas.set_callbacks (new_class)
        if (diacanvas.CanvasAbstractGroup in bases) or \
            (diacanvas.CanvasGroup in bases):
            diacanvas.set_groupable (new_class)
        return new_class

if __name__ == '__main__':
    from diacanvas import CanvasItem
    
    class MyBase(CanvasItem):
        __metaclass__ = MetaItem
        def __init__(self):
            pass

    assert hasattr (MyBase, '__gtype__')
    print MyBase.__dict__
