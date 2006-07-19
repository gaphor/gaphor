# vim:sw=4:et:

import gtk
#import diacanvas

import cairo
import cairo.svg

from gaphor.plugin import DiagramExportAction

import os
import tempfile


class PDFExportAction(DiagramExportAction):
    title = 'Export diagram to PDF file'
    ext = '.pdf'

    def save(self, filename):
        log.debug('Exporting PDF image to: %s' % filename)
        canvas = self.get_window().get_current_diagram_tab().get_canvas()
        #svg = diacanvas.ExportSVG()
        try:
            # first, export to svg
            fd, svg_name = tempfile.mkstemp()
            #svg = diacanvas.ExportSVG()
            svg.render(canvas)
            svg.save(svg_name)

            # second, convert svg to pdf
            svg = cairo.svg.Context()
            svg.parse(svg_name)
            width, height = svg.get_size()

            ctx = cairo.Context(cairo.PDFSurface(filename, width, height))
            svg.render(ctx)
            ctx.show_page()

            # svg file is no longer necessary
            os.unlink(svg_name)
        except Exception, e:
            log.error('Error while saving model to file %s: %s' % (filename, e))

