"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

import gaphor.UML as UML
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action, action_dependencies
import gtk
import diacanvas

class CloseAction(Action):
    id = 'FileClose'
    stock_id = 'gtk-close'
    tooltip='Close the diagram window'

    def init(self, window):
	self._window = window

    def execute(self):
	self._window.close()

register_action(CloseAction)


class ExportSVGAction(Action):
    id = 'FileExportSVG'
    label = '_Export SVG'
    tooltip = 'Write the contents of this diagram to a SVG file'

    def init(self, window):
	self.filename = None
	self._window = window

    def execute(self):
	filesel = gtk.FileSelection('Export diagram to SVG file')
	filesel.set_modal(True)
	filesel.set_filename(self.filename or self._window.get_diagram().name + '.svg' or 'export.svg')

	#filesel.ok_button.connect('clicked', self.on_ok_button_pressed, filesel)
	#filesel.cancel_button.connect('clicked',
	#			      self.on_cancel_button_pressed, filesel)
	
	#filesel.show()
	response = filesel.run()
	filesel.hide()
	if response == gtk.RESPONSE_OK:
	    filename = filesel.get_filename()
	    if filename and len(filename) > 0:
		self.filename = filename
		log.debug('Exporting SVG image to: %s' % filename)
		canvas = self._window.get_diagram().canvas
		export = diacanvas.ExportSVG()
		try:
		    export.render (canvas)
		    export.save(filename)
		except Exception, e:
		    log.error('Error while saving model to file %s: %s' % (filename, e))

register_action(ExportSVGAction)

class UndoStackAction(Action):
    """Dummy action that triggers the undo and redo actions to update
    themselves.
    """
    id = 'EditUndoStack'
    
    def init(self, window):
	pass

register_action(UndoStackAction)

class UndoAction(Action):
    id = 'EditUndo'
    stock_id = 'gtk-undo'
    tooltip = 'Undo the most recent changes'

    # TODO: check if the diagram can undo.

    def init(self, window):
	self._window = window
	window.get_canvas().connect('undo', self.on_undo_item)
	self.on_undo_item(window.get_canvas())

    def on_undo_item(self, canvas):
	self.sensitive = canvas.get_undo_depth() > 0

    def execute(self):
	log.debug('UndoCommand')
	self._window.get_view().canvas.pop_undo()

register_action(UndoAction)
action_dependencies(UndoAction, 'EditUndoStack')


class RedoAction(Action):
    id = 'EditRedo'
    stock_id = 'gtk-redo'
    tooltip = 'Redo the undone changes'

    def init(self, window):
	self._window = window
	window.get_canvas().connect('undo', self.on_undo_item)
	self.on_undo_item(window.get_canvas())

    def on_undo_item(self, canvas):
	self.sensitive = canvas.get_redo_depth() > 0

    def execute(self):
	self._window.get_view().canvas.pop_redo()

register_action(RedoAction)
action_dependencies(RedoAction, 'EditUndoStack')

class SelectAction(Action):
    """Dummy action that is "called" when the selected items on the canvas
    change.
    """
    id = 'ItemSelect'

    def init(self, window):
	pass

register_action(SelectAction)

class FocusAction(Action):
    """Dummy action that is "called" when the selected items on the canvas
    change.
    """
    id = 'ItemFocus'

    def init(self, window):
	pass

register_action(FocusAction)

class SelectAllAction(Action):
    id = 'EditSelectAll'
    label = '_Select all'
    accel = 'C-a'

    def init(self, window):
	self._window = window

    def execute(self):
	self._window.get_view().select_all()

register_action(SelectAllAction)

class DeselectAllAction(Action):
    id = 'EditDeselectAll'
    label = 'Des_elect all'

    def init(self, window):
	self._window = window
#	window.get_view().connect('select-item', self.on_select_item)
#	window.get_view().connect('unselect-item', self.on_select_item)
#	self.on_select_item(window.get_view(), None)

#    def on_select_item(self, view, select_item):
    def update(self):
	self.sensitive = len(self._window.get_view().selected_items) > 0

    def execute(self):
	self._window.get_view().unselect_all()

register_action(DeselectAllAction)
action_dependencies(DeselectAllAction, 'ItemSelect', 'EditDelete')


class DeleteAction(Action):
    id = 'EditDelete'
    label = '_Delete'
    accel = 'C-d'
    stock_id = 'gtk-delete'

    def init(self, window):
	self._window = window
#	window.get_view().connect('select-item', self.on_select_item)
#	window.get_view().connect('unselect-item', self.on_select_item)
#	self.on_select_item(window.get_view(), None)

#    def on_select_item(self, view, select_item):
    def update(self):
	self.sensitive = len(self._window.get_view().selected_items) > 0

    def execute(self):
	view = self._window.get_view()
	view.canvas.push_undo('delete')
	items = view.selected_items
	for i in items:
	    i.item.unlink()

register_action(DeleteAction)
action_dependencies(DeleteAction, 'ItemSelect')


class ZoomInAction(Action):
    id = 'ViewZoomIn'
    label = 'Zoom _In'
    accel = 'C-+'
    stock_id = 'gtk-zoom-in'

    def init(self, window):
	self._window = window

    def execute(self):
	view = self._window.get_view()
	view.set_zoom(view.get_zoom() + 0.1)

register_action(ZoomInAction)


class ZoomOutAction(Action):
    id = 'ViewZoomOut'
    label = 'Zoom _Out'
    stock_id = 'gtk-zoom-out'

    def init(self, window):
	self._window = window

    def execute(self):
	view = self._window.get_view()
	view.set_zoom(view.get_zoom() - 0.1)

register_action(ZoomOutAction)


class Zoom100Action(Action):
    id = 'ViewZoom100'
    label = '_Zoom 100%'
    stock_id = 'gtk-zoom-100'

    def init(self, window):
	self._window = window

    def execute(self):
	self._window.get_view().set_zoom(1.0)

register_action(Zoom100Action)


class SnapToGridAction(CheckAction):
    id = 'SnapToGrid'
    label = '_Snap to grid'

    def init(self, window):
	self._window = window
	self.active = self._window.get_view().canvas.get_property('snap_to_grid')

    def execute(self):
	self._window.get_view().canvas.set_property('snap_to_grid', self.active)

register_action(SnapToGridAction)

