
# vim:sw=4:et
import diacanvas
import gaphor.UML as UML

class PlacementTool(diacanvas.PlacementTool):

    def __init__(self, item_factory, **properties):
        """item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        diacanvas.PlacementTool.__init__(self, None, **properties)
        self.item_factory = item_factory
        self.connect ('button_press_event', self.__button_press)
        self.connect ('button_release_event', self.__button_release)

    def _create_item(self, view, event):
        if event.button == 3:
            return None

        item = self.item_factory()

        if self.properties and len(self.properties) > 0:
            try:
                for (k, v) in self.properties.items():
                    item.set_property(k, v)
            except TypeError, e:
                log.error('PlacementTool: could not set property %s' % k, e)
        return item

    def __button_press (self, tool, view, event):
        view.unselect_all()
        return 0

    def __button_release (self, tool, view, event):
        view.set_tool(None)
        return 0

