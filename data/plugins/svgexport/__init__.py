# vim:sw=4:et:

import gtk
#import diacanvas
from gaphor.plugin import DiagramExportAction


class SVGExportAction(DiagramExportAction):
    title = 'Export diagram to SVG file'
    ext = '.svg'

    def save(self, filename):
        log.debug('Exporting SVG image to: %s' % filename)
        canvas = self.get_window().get_current_diagram_tab().get_canvas()
        #export = diacanvas.ExportSVG()
        try:
            export.render (canvas)
            export.save(filename)
        except Exception, e:
            log.error('Error while saving model to file %s: %s' % (filename, e))

