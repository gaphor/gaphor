# vim:sw=4:et

from gaphor.plugin import Action

import diacanvas
import gtk

class PNGExport(Action):

    def execute(self):
        view=diacanvas.get_active_view()
        window=view.window
        (x,y,width,height,depth) = window.get_geometry()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,width,height)
        buffer=pixbuf.get_from_drawable(window, view.get_colormap(),0,0,0,0,width,height)
        buffer.save("/tmp/screenshot.png","png")
        
