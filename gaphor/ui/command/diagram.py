"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.UML as UML


class CloseCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	self._window.close()

CommandInfo (name='FileClose', _label='_Close', pixname='Close',
	     context='diagram.menu',
	     command_class=CloseCommand).register()

class ClearCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.unselect_all()

CommandInfo (name='EditClear', _label='_Clear', pixname='Clear',
	     context='diagram.menu',
	     command_class=ClearCommand).register()


class UndoCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.canvas.pop_undo()

CommandInfo (name='EditUndo', _label='_Undo', pixname='Undo', accel='*Control*z',
	     context='diagram.menu',
	     command_class=UndoCommand).register()


class RedoCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.canvas.pop_redo()

CommandInfo (name='EditRedo', _label='_Redo', pixname='Redo', accel='*Control*R',
	     context='diagram.menu',
	     command_class=RedoCommand).register()


class SelectAllCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.select_all()

CommandInfo (name='EditSelectAll', _label='_Select All', pixname='select-all',
	     context='diagram.menu',
	     command_class=SelectAllCommand).register()

class UnselectAllCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.unselect_all()

CommandInfo (name='EditUnselectAll', _label='_Clear Selection',
	     context='diagram.menu',
	     command_class=UnselectAllCommand).register()


class DeleteCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.delete_selected()
	pass

#CommandInfo (name='DiagramCreate', _label='_New diagram', pixname='gaphor-diagram',
#	     context='main.menu',
#	     command_class=CreateDiagramCommand).register()


class ZoomInCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() + 0.1)

CommandInfo (name='ViewZoomIn', _label='Zoom _In', pixname='gtk-zoom-in',
	     context='diagram.menu',
	     command_class=ZoomInCommand).register()


class ZoomOutCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() - 0.1)

CommandInfo (name='ViewZoomOut', _label='Zoom _Out', pixname='gtk-zoom-out',
	     context='diagram.menu',
	     command_class=ZoomOutCommand).register()


class Zoom100Command(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_zoom(1.0)

CommandInfo (name='ViewZoom100', _label='_Zoom 100%', pixname='gtk-zoom-100',
	     context='diagram.menu',
	     command_class=Zoom100Command).register()


class SnapToGridCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	snap = self._view.canvas.get_property ('snap_to_grid')
	self._view.canvas.set_property ('snap_to_grid', not snap)

CommandInfo (name='SnapToGrid', _label='_Snap to grid',
	     context='diagram.menu',
	     command_class=SnapToGridCommand).register()

