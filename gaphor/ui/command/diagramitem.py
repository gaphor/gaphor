# vim:sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.diagram as diagram
import gaphor.UML as UML

class PointerCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	self._window.get_view().set_tool(None)
	self._window.set_message('')

CommandInfo(name='Pointer', _label='_Pointer', context='diagram.menu',
	    _tip='Default behavior', pixname='gaphor-pointer',
	    command_class=PointerCommand).register()


class PlacementCommand(Command):
    """
    Abstract base command for commands that place an object on the canvas.
    """

    def __init__(self):
	self._name = ''
	self._class = None
	self._subject_class = None

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	assert self._class != None
	view = self._window.get_view()
	tool = diagram.PlacementTool (self._class, self._subject_class)
	view.set_tool(tool)
	self._window.set_message('Create new %s' % self._name)


class ActorPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Actor'
	self._class = diagram.ActorItem
	self._subject_class = UML.Actor

CommandInfo(name='InsertActor', _label='_Actor', context='diagram.menu',
	    _tip='Create a new Actor item', pixname='gaphor-actor',
	    command_class=ActorPlacementCommand).register()


class UseCasePlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'UseCase'
	self._class = diagram.UseCaseItem
	self._subject_class = UML.UseCase

CommandInfo(name='InsertUseCase', _label='_UseCase', context='diagram.menu',
	    _tip='Create a new Use case item', pixname='gaphor-usecase',
	    command_class=UseCasePlacementCommand).register()


class ClassPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Class'
	self._class = diagram.ClassItem
	self._subject_class = UML.Class

CommandInfo(name='InsertClass', _label='_Class', context='diagram.menu',
	    _tip='Create a new Class item', pixname='gaphor-class',
	    command_class=ClassPlacementCommand).register()


class PackagePlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Package'
	self._class = diagram.PackageItem
	self._subject_class = UML.Package

CommandInfo(name='InsertPackage', _label='_Package', context='diagram.menu',
	    _tip='Create a new Package item', pixname='gaphor-package',
	    command_class=PackagePlacementCommand).register()


class CommentPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Comment'
	self._class = diagram.CommentItem
	self._subject_class = UML.Comment

CommandInfo(name='InsertComment', _label='_Comment', context='diagram.menu',
	    _tip='Create a new Comment item', pixname='gaphor-comment',
	    command_class=CommentPlacementCommand).register()


class CommentLinePlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Comment line'
	self._class = diagram.CommentLineItem

CommandInfo(name='InsertCommentLine', _label='_Comment line', context='diagram.menu',
	    _tip='Create a new Comment line', pixname='gaphor-comment-line',
	    command_class=CommentLinePlacementCommand).register()


class AssociationPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Association'
	self._class = diagram.AssociationItem

CommandInfo(name='InsertAssociation', _label='_Association', context='diagram.menu',
	    _tip='Create a new Association', pixname='gaphor-association',
	    command_class=AssociationPlacementCommand).register()


class DependencyPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Dependency'
	self._class = diagram.DependencyItem

CommandInfo(name='InsertDependency', _label='_Dependency', context='diagram.menu',
	    _tip='Create a new Dependency', pixname='gaphor-dependency',
	    command_class=DependencyPlacementCommand).register()


class GeneralizationPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self._name = 'Generalization'
	self._class = diagram.GeneralizationItem

CommandInfo(name='InsertGeneralization', _label='_Generalization', context='diagram.menu',
	    _tip='Create a new Generalization item', pixname='gaphor-generalization',
	    command_class=GeneralizationPlacementCommand).register()


