# vim:sw=4
"""Menu actions that create diagram items.

This module is initialized from gaphor.ui.diagramwindow
"""
import gaphor
import gaphor.UML as UML
import gaphor.diagram as diagram
from gaphor.misc.action import Action, CheckAction, RadioAction
from gaphor.misc.action import register_action as _register_action
from gaphor.misc.action import action_dependencies as _action_dependencies

def register_action(action, *args):
    _register_action(action, *args)
    _action_dependencies(action, 'ToolChange', 'TabChange', 'OpenModelElement')

def tool_changed(action, window):
    view = window.get_current_diagram_view()
    if not view:
	action.sensitive = False
	return
    else:
	action.sensitive = True
    tool = view.get_property('tool')
    if tool:
	id = tool.action_id
    else:
	id = 'Pointer'
    if id == action.id:
	action.active = True


class PointerAction(RadioAction):
    id = 'Pointer'
    label = '_Pointer'
    stock_id = 'gaphor-pointer'
    group = 'placementtools'
    accel = 'C-p'
    tooltip = 'Pointer'

    def init(self, window):
	self._window = window
	#self._window.get_current_diagram_view().connect('notify::tool', tool_changed, window)

    def update(self):
	tool_changed(self, self._window)

    def execute(self):
	self._window.get_current_diagram_view().set_tool(None)
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

    def update(self):
	tool_changed(self, self._window)

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = self._window.get_current_diagram().create(self.type)
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
	self._window.get_current_diagram_view().set_tool(tool)
	self._window.set_message('Create new %s' % self.name)


class NamespacePlacementAction(PlacementAction):

    def item_factory(self):
	"""Create a new instance of the item and return it."""
        item = PlacementAction.item_factory(self)
	item.subject.package = self._window.get_current_diagram().namespace
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
    accel = 'C-c'
    type = diagram.ClassItem
    subject_type = UML.Class

register_action(ClassPlacementAction)

class StereotypePlacementAction(NamespacePlacementAction):
    id = 'InsertStereotype'
    label = '_Stereotype'
    tooltip = 'Create a new Stereotype item'
    stock_id = 'gaphor-stereotype'
    name = 'Stereotype'
    accel = 'C-c'
    type = diagram.ClassItem
    subject_type = UML.Stereotype

register_action(StereotypePlacementAction)


class PackagePlacementAction(NamespacePlacementAction):
    id = 'InsertPackage'
    label = '_Package'
    tooltip = 'Create a new Package item'
    stock_id = 'gaphor-package'
    name = 'Package'
    type = diagram.PackageItem
    subject_type = UML.Package

register_action(PackagePlacementAction)


class InitialNodePlacementAction(PlacementAction):
    id = 'InsertInitialNode'
    label = 'Initial node'
    tooltip = 'Create a new Initial action node'
    stock_id = 'gaphor-initial-node'
    name = 'InitialNode'
    type = diagram.InitialNodeItem
    subject_type = UML.InitialNode

register_action(InitialNodePlacementAction)


class ActivityFinalNodePlacementAction(PlacementAction):
    id = 'InsertActivityFinalNode'
    label = 'Final activity node'
    tooltip = 'Create a new Final activity node'
    stock_id = 'gaphor-activity-final-node'
    name = 'ActivityFinalNode'
    type = diagram.ActivityFinalNodeItem
    subject_type = UML.ActivityFinalNode

register_action(ActivityFinalNodePlacementAction)


class DecisionNodePlacementAction(PlacementAction):
    id = 'InsertDecisionNode'
    label = 'Decision node'
    tooltip = 'Create a new Decision action node'
    stock_id = 'gaphor-decision-node'
    name = 'DecisionNode'
    type = diagram.DecisionNodeItem
    subject_type = UML.DecisionNode

register_action(DecisionNodePlacementAction)


class ActionPlacementAction(PlacementAction):
    id = 'InsertAction'
    label = 'Action node'
    tooltip = 'Create a new Action node'
    stock_id = 'gaphor-action'
    name = 'Action'
    type = diagram.ActionItem
    subject_type = UML.Action

register_action(ActionPlacementAction)


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

register_action(AssociationPlacementAction)


class ExtensionPlacementAction(PlacementAction):
    id = 'InsertExtension'
    label = '_Extension'
    tooltip = 'Create a new Extension line'
    stock_id = 'gaphor-extension'
    name = 'Extension'
    type = diagram.ExtensionItem

register_action(ExtensionPlacementAction)


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


class FlowPlacementAction(PlacementAction):
    id = 'InsertFlow'
    label = '_Flow'
    tooltip = 'Create a Flow'
    stock_id = 'gaphor-control-flow'
    name = 'Flow'
    type = diagram.FlowItem

register_action(FlowPlacementAction)

