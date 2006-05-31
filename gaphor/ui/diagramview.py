# vim: sw=4

import gobject
import gtk
from diacanvas import CanvasView

class DiagramView(CanvasView):
    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        ('gaphor/element-id', 0, TARGET_ELEMENT_ID)]

    def __init__(self, diagram=None):
        self.__gobject_init__()

        if diagram:
            canvas = diagram.canvas
        else:
            canvas = None
        CanvasView.__init__(self, canvas)
#        self.diagram = diagram
        # Drop
        self.drag_dest_set (gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)

gobject.type_register(DiagramView)
