"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command, StatefulCommand
from commandinfo import CommandInfo
import gaphor.UML as UML
import gtk
import diacanvas

class CloseCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	self._window.close()

CommandInfo (name='FileClose', _label='_Close', pixname='Close',
	     _tip='Close the diagram window',
	     accel='*Control*w',
	     context='diagram.menu',
	     command_class=CloseCommand).register()


class ExportSVGCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def set_parameters(self, params):
	self._window = params['window']

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

#    def on_ok_button_pressed(self, button, filesel):
#	filename = filesel.get_filename()
#	filesel.destroy()
#	if filename and len(filename) > 0:
#	    log.debug('Exporting SVG image to: %s' % filename)
#	    canvas = self._window.get_diagram().canvas
#	    export = diacanvas.ExportSVG()
#	    try:
#		export.render (canvas)
#		export.save(filename)
#	    except Exception, e:
#		log.error('Error while saving model to file %s: %s' % (filename, e))

#    def on_cancel_button_pressed(self, button, filesel):
#	filesel.destroy()

CommandInfo (name='FileExportSVG', _label='_Export SVG...', pixname='Export',
	     _tip='Save the current diagram to a SVG file',
	     context='diagram.menu',
	     command_class=ExportSVGCommand).register()


class ClearCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.unselect_all()

CommandInfo (name='EditClear', _label='_Clear', pixname='Clear',
	     _tip='Clear the selection',
	     context='diagram.menu',
	     command_class=ClearCommand).register()


class UndoCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	log.debug('UndoCommand')
	self._view.canvas.pop_undo()

CommandInfo (name='EditUndo', _label='_Undo', pixname='Undo', accel='*Control*z',
	     _tip='Undo the most recent changes',
	     context='diagram.menu', sensitive=('undo',),
	     command_class=UndoCommand).register()


class RedoCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.canvas.pop_redo()

CommandInfo (name='EditRedo', _label='_Redo', pixname='Redo', accel='*Control*R',
	     _tip='Redo the undone changes',
	     context='diagram.menu', sensitive=('redo',),
	     command_class=RedoCommand).register()


class SelectAllCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.select_all()

CommandInfo (name='EditSelectAll', _label='_Select All', pixname='select-all',
	     context='diagram.menu', accel='*Control*a',
	     command_class=SelectAllCommand).register()

class UnselectAllCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.unselect_all()

CommandInfo (name='EditUnselectAll', _label='_Clear Selection',
	     context='diagram.menu', sensitive=('select',),
	     command_class=UnselectAllCommand).register()


class DeleteCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.canvas.push_undo('delete')
	items = self._view.selected_items
	for i in items:
	    i.item.unlink()

CommandInfo (name='EditDelete', _label='_Delete', pixname='gtk-delete',
	     context='diagram.menu', accel='*Control*d',
	     sensitive=('select',),
	     command_class=DeleteCommand).register()


class ZoomInCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() + 0.1)

CommandInfo (name='ViewZoomIn', _label='Zoom _In', pixname='gtk-zoom-in',
	     context='diagram.menu', accel='*Control*plus',
	     command_class=ZoomInCommand).register()


class ZoomOutCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() - 0.1)

CommandInfo (name='ViewZoomOut', _label='Zoom _Out', pixname='gtk-zoom-out',
	     context='diagram.menu', accel='*Control*minus',
	     command_class=ZoomOutCommand).register()


class Zoom100Command(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(1.0)

CommandInfo (name='ViewZoom100', _label='_Zoom 100%', pixname='gtk-zoom-100',
	     context='diagram.menu',
	     command_class=Zoom100Command).register()


class SnapToGridCommand(StatefulCommand):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self, snap):
	#snap = self._view.canvas.get_property ('snap_to_grid')
	self._view.canvas.set_property ('snap_to_grid', snap)
	log.debug('Snap to grid set to %d' % self._view.canvas.get_property('snap_to_grid'))

CommandInfo (name='SnapToGrid', _label='_Snap to grid',
	     context='diagram.menu', state=('snap_to_grid',),
	     command_class=SnapToGridCommand).register()

