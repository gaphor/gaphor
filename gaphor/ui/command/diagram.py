"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command
import gaphor.UML as UML

class CreateDiagramCommand(Command):

    def execute(self):
	elemfact = GaphorResource(UML.ElementFactory)
	model = elemfact.lookup(1) # model
	diagram = elemfact.create(UML.Diagram)
	diagram.namespace = model
	diagram.name = "New diagram"

class _CanvasViewCommand(Command):

    def __init__(self, view, **args):
	Command.__init__(self)
	self._view = view


class UndoCommand(_CanvasViewCommand):

    def execute(self):
	self._view.canvas.pop_undo()


class RedoCommand(_CanvasViewCommand):

    def execute(self):
	self._view.canvas.pop_redo()


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


class PlacementCommand(_CanvasViewCommand):

    def __init__(self, view, diagram, klass):
	_CanvasViewCommand.__init__(self, view)
	self._diagram = diagram
	self._klass = klass

    def execute(self):
	from gaphor.ui.placementtool import PlacementTool
	tool = PlacementTool (self._diagram, self._klass)
	self._view.set_tool(tool)

