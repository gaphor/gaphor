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
    """Abstract base command for commands that place an object on the canvas.
    """

    def __init__(self):
	self.name = ''
	self.type = None
	self.subject_type = None

    def set_parameters(self, params):
	self._window = params['window']

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = self._window.get_diagram().create(self.type)
	if self.subject_type:
	    subject = GaphorResource('ElementFactory').create(self.subject_type)
	    try:
		print 'set subject'
		#item.set_property('subject', subject)
		item.subject = subject
		print 'set subject done'
	    except Exception, e:
		print 'ERROR:', e
	return item

    def execute(self):
	assert self.type != None
	tool = diagram.PlacementTool(self.item_factory)
	self._window.get_view().set_tool(tool)
	self._window.set_message('Create new %s' % self.name)


class NamespacePlacementCommand(PlacementCommand):

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = PlacementCommand.item_factory(self)
	item.subject.package = self._window.get_diagram().namespace
	return item


class ActorPlacementCommand(NamespacePlacementCommand):

    def __init__(self):
	NamespacePlacementCommand.__init__(self)
	self.name = 'Actor'
	self.type = diagram.ActorItem
	self.subject_type = UML.Actor

CommandInfo(name='InsertActor', _label='_Actor', context='diagram.menu',
	    _tip='Create a new Actor item', pixname='gaphor-actor',
	    command_class=ActorPlacementCommand).register()


class UseCasePlacementCommand(NamespacePlacementCommand):

    def __init__(self):
	NamespacePlacementCommand.__init__(self)
	self.name = 'UseCase'
	self.type = diagram.UseCaseItem
	self.subject_type = UML.UseCase

CommandInfo(name='InsertUseCase', _label='_UseCase', context='diagram.menu',
	    _tip='Create a new Use case item', pixname='gaphor-usecase',
	    command_class=UseCasePlacementCommand).register()


class ClassPlacementCommand(NamespacePlacementCommand):

    def __init__(self):
	NamespacePlacementCommand.__init__(self)
	self.name = 'Class'
	self.type = diagram.ClassItem
	self.subject_type = UML.Class

CommandInfo(name='InsertClass', _label='_Class', context='diagram.menu',
	    _tip='Create a new Class item', pixname='gaphor-class',
	    command_class=ClassPlacementCommand).register()


class PackagePlacementCommand(NamespacePlacementCommand):

    def __init__(self):
	NamespacePlacementCommand.__init__(self)
	self.name = 'Package'
	self.type = diagram.PackageItem
	self.subject_type = UML.Package

CommandInfo(name='InsertPackage', _label='_Package', context='diagram.menu',
	    _tip='Create a new Package item', pixname='gaphor-package',
	    command_class=PackagePlacementCommand).register()


class CommentPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self.name = 'Comment'
	self.type = diagram.CommentItem
	self.subject_type = UML.Comment

CommandInfo(name='InsertComment', _label='_Comment', context='diagram.menu',
	    _tip='Create a new Comment item', pixname='gaphor-comment',
	    command_class=CommentPlacementCommand).register()


class CommentLinePlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self.name = 'Comment line'
	self.type = diagram.CommentLineItem

CommandInfo(name='InsertCommentLine', _label='_Comment line', context='diagram.menu',
	    _tip='Create a new Comment line', pixname='gaphor-comment-line',
	    command_class=CommentLinePlacementCommand).register()


class AssociationPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self.name = 'Association'
	self.type = diagram.AssociationItem

CommandInfo(name='InsertAssociation', _label='_Association', context='diagram.menu',
	    _tip='Create a new Association', pixname='gaphor-association',
	    command_class=AssociationPlacementCommand).register()


class DependencyPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self.name = 'Dependency'
	self.type = diagram.DependencyItem

CommandInfo(name='InsertDependency', _label='_Dependency', context='diagram.menu',
	    _tip='Create a new Dependency', pixname='gaphor-dependency',
	    command_class=DependencyPlacementCommand).register()


class GeneralizationPlacementCommand(PlacementCommand):

    def __init__(self):
	PlacementCommand.__init__(self)
	self.name = 'Generalization'
	self.type = diagram.GeneralizationItem

CommandInfo(name='InsertGeneralization', _label='_Generalization', context='diagram.menu',
	    _tip='Create a new Generalization item', pixname='gaphor-generalization',
	    command_class=GeneralizationPlacementCommand).register()


