"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command
import gaphor.UML as UML


class _CanvasViewCommand(Command):

    def __init__(self, view):
	Command.__init__(self)
	self._view = view


class UndoCommand(_CanvasViewCommand):

    def execute(self):
	self._view.pop_undo()


class RedoCommand(_CanvasViewCommand):

    def execute(self):
	self._view.pop_redo()


class DeleteCommand(_CanvasViewCommand):

    def execute(self):
	#self._view.delete_selected()
	pass


class ZoomInCommand(_CanvasViewCommand):

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() + 0.1)


class ZoomOutCommand(_CanvasViewCommand):

    def execute(self):
	self._view.set_zoom(self._view.get_zoom() - 0.1)


class Zoom100Command(_CanvasViewCommand):

    def execute(self):
	self._view.set_zoom(1.0)


class SnapToGridCommand(_CanvasViewCommand):

    def execute(self):
	snap = self._view.canvas.get_property ('snap_to_grid')
	view.canvas.set_property ('snap_to_grid', not snap)

