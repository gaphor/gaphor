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
import diacanvas as dia
#from diacanvas import set_callbacks, set_groupable
#from diacanvas import CanvasItem, CanvasGroup, CanvasAbstractGroup, \
#		CanvasLine, CanvasElement, CanvasBox, CanvasText, CanvasImage

class MetaItem (type):
    def __new__ (self, name, bases, members):
	new_class = type.__new__ (self, name, bases, members)
	print 'MetaItem:', new_class
	gobject.type_register (new_class)
	if (dia.CanvasItem in bases) or \
	    (dia.CanvasGroup in bases) or \
	    (dia.CanvasLine in bases) or \
	    (dia.CanvasElement in bases) or \
	    (dia.CanvasBox in bases) or \
	    (dia.CanvasText in bases) or \
	    (dia.CanvasImage in bases):
	    dia.set_callbacks (new_class)
	if (dia.CanvasAbstractGroup in bases) or \
	    (dia.CanvasGroup in bases):
	    dia.set_groupable (new_class)
	return new_class

if __name__ == '__main__':
    from diacanvas import CanvasItem
    
    class MyBase(CanvasItem):
	__metaclass__ = MetaItem
	def __init__(self):
	    pass

    assert hasattr (MyBase, '__gtype__')
    print MyBase.__dict__
