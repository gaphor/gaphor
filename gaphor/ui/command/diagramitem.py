# vim:sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.diagram as diagram
import gaphor.UML as UML

class UnsetPlacementCommand(Command):

    def set_parameters(self, params):
	self._view = params['window'].get_view()

    def execute(self):
	self._view.set_tool(None)


class PlacementCommand(Command):
    """
    Abstract base command for commands that place an object on the canvas.
    """

    def __init__(self):
	self._class = None
	self._subject_class = None

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	assert self._class != None
	view = self._window.get_view()
	tool = diagram.PlacementTool (self._class, self._subject_class)
	view.set_tool(tool)

class ActorPlacementCommand(PlacementCommand):

    def __init__(self):
	self._class = diagram.ActorItem
	self._subject_class = UML.Actor

CommandInfo(name='InsertActor', _label='_Actor', context='diagram.menu',
	    _tip='Create a new Actor item', pixname='gaphor-actor',
	    command_class=ActorPlacementCommand).register()


class UseCasePlacementCommand(PlacementCommand):

    def __init__(self):
	self._class = diagram.UseCaseItem
	self._subject_class = UML.UseCase

CommandInfo(name='InsertUseCase', _label='_Use Case', context='diagram.menu',
	    _tip='Create a new Use case item', pixname='gaphor-usecase',
	    command_class=UseCasePlacementCommand).register()


class ClassPlacementCommand(PlacementCommand):

    def __init__(self):
	self._class = diagram.ClassItem
	self._subject_class = UML.Class

CommandInfo(name='InsertClass', _label='_Class', context='diagram.menu',
	    _tip='Create a new Class item', pixname='gaphor-class',
	    command_class=ClassPlacementCommand).register()


