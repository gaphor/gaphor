
# vim:sw=4:et:ai
"""
Test a simple diagram item.

Bugs:
- When editing text, the mouse cursor is not visible when hovering over the text
- `Enter' should end editing in most cases.
"""

from __future__ import generators

import pygtk
pygtk.require('2.0')

import gobject
import gtk
import diacanvas
import gaphor
import gaphor.UML as UML
import gaphor.diagram as diagram

class TestItem(diacanvas.CanvasBox, diacanvas.CanvasEditable):

    def __init__(self):
        self.__gobject_init__()
        self.set(width=100, height=100)
        self._text = diacanvas.shape.Text()

    def on_event(self, event):
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            self.start_editing(self._text)
            return True
        else:
            return diacanvas.CanvasBox.on_event(self, event)

    def on_update(self, affine):
        diacanvas.CanvasBox.on_update(self, affine)
        #self._text.set_max_width(self.width)
        #self._text.set_max_height(self.height)
        #self._text.set_text_width(self.width)

    def on_shape_iter(self):
        for i in diacanvas.CanvasBox.on_shape_iter(self):
            yield i
        yield self._text

    # CanvasEditable:

    def on_editable_editing_done(self, shape, new_text):
        self._text.set_text(new_text)
        self.request_update()

gobject.type_register(TestItem)
diacanvas.set_callbacks(TestItem)
diacanvas.set_editable(TestItem)

class TestItem2(diacanvas.CanvasBox, diacanvas.CanvasGroupable):

    def __init__(self):
        self.__gobject_init__()
        self.set(width=100, height=100)
        self._text = diacanvas.CanvasText()
        self._text.set_child_of(self)

    def on_update(self, affine):
        diacanvas.CanvasBox.on_update(self, affine)
        self._text.set(width=self.width, height=self.height)
        self.update_child(self._text, affine)

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        pass

    def on_groupable_iter(self):
        yield self._text
        
    def on_groupable_length(self):
        return 1

    def on_groupable_pos(self, item):
        return self._text is item and 0 or -1

gobject.type_register(TestItem2)
diacanvas.set_callbacks(TestItem2)
diacanvas.set_groupable(TestItem2)

def mainquit(*args): gtk.main_quit()

def create_window(canvas):
    win = gtk.Window()
    win.connect('destroy', mainquit)
    view = diacanvas.CanvasView(canvas)
    win.add(view)
    view.show()
    win.show()

canvas = diacanvas.Canvas()
factory = gaphor.resource('ElementFactory')

package = factory.create(UML.Package)
item = diagram.PackageItem()
item.subject = package
canvas.root.add(item)

item = TestItem()
item.move(0,100)
canvas.root.add(item)

item = TestItem2()
item.move(100,100)
canvas.root.add(item)

create_window(canvas)

gtk.main()


