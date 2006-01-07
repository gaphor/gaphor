# vim:sw=4:et

from gaphor.plugin import DiagramExportAction

import diacanvas
import gtk

class PNGExport(DiagramExportAction):
    title = 'Export diagram to PNG file'
    ext = '.png'

    def save(self, filename):
        view = self.get_window().get_current_diagram_view()
        #view=diacanvas.get_active_view()
        window = view.window
        # Should use canvas geometry:
        (x,y,width,height,depth) = window.get_geometry()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,width,height)
        buffer = pixbuf.get_from_drawable(window, view.get_colormap(),
                                          0, 0, 0, 0, width, height)
        buffer.save(filename, "png")
        
