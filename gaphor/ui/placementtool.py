
# vim:sw=4:
import diacanvas
import gaphor.diagram as diagram

class PlacementTool(diacanvas.PlacementTool):

    def __init__(self, diagram, type, **properties):
	diacanvas.PlacementTool.__init__(self, type, **properties)
	self.diagram = diagram
	self.connect ('button_press_event', self.__button_press)
	self.connect ('button_release_event', self.__button_release)

    def _create_item(self):
	f = diagram.DiagramItemFactory()
	item = f.create(self.diagram, self.type)
	if self.properties and len(self.properties) > 0:
            try:
                for (k,v) in self.properties.items():
                    item.set_property(k, v)
            except TypeError, e:
                print 'PlacementTool:', e
        return item

    def __button_press (self, tool, view, event):
	view.unselect_all()
	return 0

    def __button_release (self, tool, view, event):
	view.set_tool (None)
	return 0

