# vim:sw=4
"""Menu actions that create diagram items.

This module is initialized from gaphor.ui.diagramwindow
"""
import gaphor
import gaphor.UML as UML
import gaphor.diagram as diagram
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action

def tool_changed(view, pspec, window):
    tool = view.get_property('tool')
    if tool:
	id = tool.action_id
    else:
	id = 'Pointer'
    action = window.menu_factory.get_action(id)
    action.active = True

class PointerAction(RadioAction):
    id = 'Pointer'
    label = '_Pointer'
    stock_id = 'gaphor-pointer'
    group = 'placementtools'
    accel = 'C-p'

    def init(self, window):
	self._window = window
	self._window.get_view().connect('notify::tool', tool_changed, window)

    def execute(self):
	self._window.get_view().set_tool(None)
	self._window.set_message('')

register_action(PointerAction)


class PlacementAction(RadioAction):
    """Abstract base command for commands that place an object on the canvas.
    """
    name = ''
    type = None
    subject_type = None
    group = 'placementtools'

    def init(self, window):
	self._window = window

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = self._window.get_diagram().create(self.type)
	if self.subject_type:
	    subject = gaphor.resource('ElementFactory').create(self.subject_type)
	    try:
		#print 'set subject'
		#item.set_property('subject', subject)
		item.subject = subject
		#print 'set subject done'
	    except Exception, e:
		print 'ERROR:', e
	return item

    def execute(self):
	assert self.type != None
	tool = diagram.PlacementTool(self.item_factory, self.id)
	self._window.get_view().set_tool(tool)
	self._window.set_message('Create new %s' % self.name)


class NamespacePlacementAction(PlacementAction):

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = PlacementAction.item_factory(self)
	item.subject.package = self._window.get_diagram().namespace
	return item


class ActorPlacementAction(NamespacePlacementAction):
    id = 'InsertActor'
    label = '_Actor'
    stock_id = 'gaphor-actor'
    tooltip = 'Create a new Actor item'
    name = 'Actor'
    type = diagram.ActorItem
    subject_type = UML.Actor

register_action(ActorPlacementAction)


class UseCasePlacementAction(NamespacePlacementAction):
    id = 'InsertUseCase'
    label = '_UseCase'
    tooltip = 'Create a new Use case item'
    stock_id = 'gaphor-usecase'
    name = 'UseCase'
    type = diagram.UseCaseItem
    subject_type = UML.UseCase

register_action(UseCasePlacementAction)


class ClassPlacementAction(NamespacePlacementAction):
    id = 'InsertClass'
    label = '_Class'
    tooltip = 'Create a new Class item'
    stock_id = 'gaphor-class'
    name = 'Class'
    type = diagram.ClassItem
    subject_type = UML.Class

register_action(ClassPlacementAction)


class PackagePlacementAction(NamespacePlacementAction):
    id = 'InsertPackage'
    label = '_Package'
    tooltip = 'Create a new Package item'
    stock_id = 'gaphor-package'
    name = 'Package'
    type = diagram.PackageItem
    subject_type = UML.Package

register_action(PackagePlacementAction)


class CommentPlacementAction(PlacementAction):
    id = 'InsertComment'
    label = 'C_omment'
    tooltip = 'Create a new Comment item'
    stock_id = 'gaphor-comment'
    name = 'Comment'
    type = diagram.CommentItem
    subject_type = UML.Comment

register_action(CommentPlacementAction)


class CommentLinePlacementAction(PlacementAction):
    id = 'InsertCommentLine'
    label = 'Comment _line'
    tooltip = 'Create a new Comment line'
    stock_id = 'gaphor-comment-line'
    name = 'Comment line'
    type = diagram.CommentLineItem

register_action(CommentLinePlacementAction)


class AssociationPlacementAction(PlacementAction):
    id = 'InsertAssociation'
    label = '_Association'
    tooltip = 'Create a new Association line'
    stock_id = 'gaphor-association'
    name = 'Association'
    type = diagram.AssociationItem

    def __init__(self):
	PlacementAction.__init__(self)

register_action(AssociationPlacementAction)


class DependencyPlacementAction(PlacementAction):
    id = 'InsertDependency'
    label = '_Dependency'
    tooltip = 'Create a new Dependency'
    stock_id = 'gaphor-dependency'
    name = 'Dependency'
    type = diagram.DependencyItem

register_action(DependencyPlacementAction)


class GeneralizationPlacementAction(PlacementAction):
    id = 'InsertGeneralization'
    label = '_Generalization'
    tooltip = 'Create a new Generalization'
    stock_id = 'gaphor-generalization'
    name = 'Generalization'
    type = diagram.GeneralizationItem

register_action(GeneralizationPlacementAction)

