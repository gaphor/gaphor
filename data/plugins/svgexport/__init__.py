# vim:sw=4:et:

import gtk
import diacanvas
from gaphor.plugin import Action


class SVGExportAction(Action):

    def update(self):
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False

    def execute(self):
        filesel = gtk.FileSelection('Export diagram to SVG file')
        filesel.set_modal(True)
        filesel.set_filename((self.get_window().get_current_diagram().name or 'export') + '.svg')

        response = filesel.run()
        filesel.hide()
        if response == gtk.RESPONSE_OK:
            filename = filesel.get_filename()
            if filename and len(filename) > 0:
                log.debug('Exporting SVG image to: %s' % filename)
                canvas = self.get_window().get_current_diagram_tab().get_canvas()
                export = diacanvas.ExportSVG()
                try:
                    export.render (canvas)
                    export.save(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))

