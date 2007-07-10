"""
Service dedicated to exporting diagrams to a varyity of file formats.
"""

import os
from zope import interface, component
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider

import cairo
from gaphas.view import View
from gaphas.painter import ItemPainter
from gaphas.geometry import Rectangle

class DiagramExportManager(object):
    """
    Service for exporting diagrams as images (SVG, PNG, PDF).
    """

    interface.implements(IService, IActionProvider)

    gui_manager = inject('gui_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="file">
            <menu action="file-export">
              <menuitem action="file-export-svg" />
              <menuitem action="file-export-png" />
              <menuitem action="file-export-pdf" />
              <separator />
            </menu>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    def update(self):
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False


    def save_dialog(self, diagram, title, ext):
        import gtk
        filename = (diagram.name or 'export') + ext

        filesel = gtk.FileChooserDialog(title = title,
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        filesel.set_current_name(filename)

        save = False
        while True:
            response = filesel.run()
            filename = filesel.get_filename()

            if response == gtk.RESPONSE_OK:
                if os.path.exists(filename):
                    dialog = gtk.MessageDialog(filesel,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                        _("The file %s already exists. Do you want to replace it with the file you are exporting to?") % filename)
                    answer = dialog.run()
                    dialog.destroy()
                    if answer == gtk.RESPONSE_YES:
                        save = True
                        break
                else:
                    save = True
                    break
            else:
                break

        filesel.destroy()

        if save and filename:
            return filename
        return None


    def save_svg(self, filename, canvas):
        log.debug('Exporting SVG image to: %s' % filename)
        view = View(canvas)
        view.painter = ItemPainter()

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.SVGSurface(filename, w, h)
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.flush()
        surface.finish()


    def save_png(self, filename, canvas):
        log.debug('Exporting PNG image to: %s' % filename)
        view = View(canvas)
        view.painter = ItemPainter()

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr, items=canvas.get_root_items())
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w+1), int(h+1))
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.write_to_png(filename)

    def save_pdf(self, filename, canvas):
        log.debug('Exporting PDF image to: %s' % filename)
        view = View(canvas)
        view.painter = ItemPainter()

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.PDFSurface(filename, w, h)
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.flush()
        surface.finish()

    @action(name='file-export-svg', label='Export to SVG',
            tooltip='Export the diagram to SVG')
    def save_svg_action(self):
        title = 'Export diagram to SVG'
        ext = '.svg'
        diagram = self.gui_manager.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_svg(filename, diagram.canvas)


    @action(name='file-export-png', label='Export to PNG',
            tooltip='Export the diagram to PNG')
    def save_png_action(self):
        title = 'Export diagram to PNG'
        ext = '.png'
        diagram = self.gui_manager.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_png(filename, diagram.canvas)


    @action(name='file-export-pdf', label='Export to PDF',
            tooltip='Export the diagram to PDF')
    def save_pdf_action(self):
        title = 'Export diagram to PDF'
        ext = '.pdf'
        diagram = self.gui_manager.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_pdf(filename, diagram.canvas)


# vim:sw=4:et:

