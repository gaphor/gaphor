
import cairo
from gaphor.plugin import DiagramExportAction
from gaphas.view import View
from gaphas.painter import ItemPainter
from gaphas.geometry import Rectangle

class SVGExportAction(DiagramExportAction):
    title = 'Export diagram to SVG file'
    ext = '.svg'

    def save(self, filename, canvas=None):
        log.debug('Exporting SVG image to: %s' % filename)
        canvas = canvas or self.get_window().get_current_diagram_tab().get_canvas()
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
        view.matrix.translate(-view.bounding_box.x0, -view.bounding_box.y0)
        view.paint(cr)
        cr.show_page()
        surface.flush()
        surface.finish()


if __name__ == '__main__':
    from gaphor.diagram import items
    from gaphor.ui.mainwindow import MainWindow
    import gaphas

    canvas = gaphas.Canvas()
    canvas.add(items.ClassItem())

    export = SVGExportAction()
    export.save('svgexport.svg', canvas)

# vim:sw=4:et:
