
# vim:sw=4:
import diacanvas
import gaphor.UML as UML

class PlacementTool(diacanvas.PlacementTool):

    def __init__(self, type, subject_class, **properties):
	diacanvas.PlacementTool.__init__(self, type, **properties)
	self.subject_class = subject_class
	self.connect ('button_press_event', self.__button_press)
	self.connect ('button_release_event', self.__button_release)

    def _create_item(self, view, event):
	if event.button == 3:
	    return None
	elemfact = GaphorResource('ElementFactory')
	item = view.get_diagram().create(self.type)
	if self.subject_class:
	    subject = elemfact.create(self.subject_class)
	    item.set_property ('subject', subject)
	    if isinstance(subject, UML.Namespace):
		subject.package = view.get_diagram().namespace

	if self.properties and len(self.properties) > 0:
            try:
                for (k,v) in self.properties.items():
                    item.set_property(k, v)
            except TypeError, e:
                log.error('PlacementTool:', e)
        return item

    def __button_press (self, tool, view, event):
	view.unselect_all()
	return 0

    def __button_release (self, tool, view, event):
	view.set_tool (None)
	return 0

