# vim:sw=4:et

from gaphor.plugin import Action

import diacanvas
import gtk

class PNGExport(Action):

    def update(self):
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False

    def execute(self):
        if gtk.gtk_version < (2, 4, 0):
            filesel = gtk.FileSelection('Export diagram to PNG file')
        else:
            filesel = gtk.FileChooserDialog(title='Export diagram to PNG file',
                                            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        filesel.set_filename((self.get_window().get_current_diagram().name or 'export') + '.png')

        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if response == gtk.RESPONSE_OK:
            if filename and len(filename) > 0:
                view = self.get_window().get_current_diagram_view()
                #view=diacanvas.get_active_view()
                window = view.window
                # Should use canvas geometry:
                (x,y,width,height,depth) = window.get_geometry()
                pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,width,height)
                buffer = pixbuf.get_from_drawable(window, view.get_colormap(),
                                                  0, 0, 0, 0, width, height)
                buffer.save(filename, "png")
        
