# vim:sw=4
"""Menu actions that create diagram items.

This module is initialized from gaphor.ui.diagramwindow
"""

import gaphas
from gaphor import resource
from gaphor import UML
from gaphor import diagram
from gaphor.diagram import usecase
from gaphor.diagram.tool import DefaultTool, PlacementTool
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
    tool = None #view.tool
    if tool:
        id = tool.action_id
    else:
        id = 'Pointer'
    if id == action.id:
        action.active = True


class ResetToolAfterCreateAction(CheckAction):
    id = 'ResetToolAfterCreate'
    label = 'Reset _Tool'
    tooltip = 'Reset the tool to the pointer tool after creation of an item'

    def init(self, window):
        self._window = window
        self.active = resource('reset-tool-after-create', True)

    def execute(self):
        resource.set('reset-tool-after-create', self.active, persistent=True)

register_action(ResetToolAfterCreateAction)


class PointerAction(RadioAction):
    id = 'Pointer'
    label = '_Pointer'
    stock_id = 'gaphor-pointer'
    group = 'placementtools'
    accel = 'C-p'
    tooltip = 'Pointer'

    def init(self, window):
        self._window = window

    def update(self):
        tool_changed(self, self._window)

    def execute(self):
        self._window.get_current_diagram_view().tool = DefaultTool()
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
        subject = None
        if self.subject_type:
            subject = resource(UML.ElementFactory).create(self.subject_type)
        diagram = self._window.get_current_diagram()
        return diagram.create(self.type, subject=subject)

    def execute(self):
        assert self.type != None
        tool = PlacementTool(item_factory=self.item_factory, action_id=self.id)
        self._window.get_current_diagram_view().tool = tool
        self._window.set_message('Create new %s' % self.name)


class NamespacePlacementAction(PlacementAction):
    __index = 1

    def item_factory(self):
        """Create a new instance of the item and return it."""
        item = PlacementAction.item_factory(self)
        #log.debug('Setting namespace for new item %s: %s' % (item, self._window.get_current_diagram().namespace))
        item.subject.package = self._window.get_current_diagram().namespace
        item.subject.name = '%s%d' % (self.name, self.__index)
        item.request_update()
        self.__index += 1
        return item


class ActorPlacementAction(NamespacePlacementAction):
    id = 'InsertActor'
    label = '_Actor'
    stock_id = 'gaphor-actor'
    tooltip = 'Create a new actor item'
    name = 'Actor'
    type = diagram.ActorItem
    subject_type = UML.Actor

register_action(ActorPlacementAction)


class UseCasePlacementAction(NamespacePlacementAction):
    id = 'InsertUseCase'
    label = '_UseCase'
    tooltip = 'Create a new use case item'
    stock_id = 'gaphor-usecase'
    name = 'UseCase'
    type = diagram.usecase.UseCaseItem
    subject_type = UML.UseCase

register_action(UseCasePlacementAction)


#class IncludePlacementAction(PlacementAction):
#    id = 'InsertInclude'
#    label = '_Include'
#    tooltip = 'Create a new include'
#    stock_id = 'gaphor-include'
#    name = 'Include'
#    type = diagram.IncludeItem
#
#register_action(IncludePlacementAction)


#class ExtendPlacementAction(PlacementAction):
#    id = 'InsertExtend'
#    label = '_Extend'
#    tooltip = 'Create a new extend'
#    stock_id = 'gaphor-extend'
#    name = 'Extend'
#    type = diagram.ExtendItem
#
#register_action(ExtendPlacementAction)


#class ClassPlacementAction(NamespacePlacementAction):
#    id = 'InsertClass'
#    label = '_Class'
#    tooltip = 'Create a new class item'
#    stock_id = 'gaphor-class'
#    name = 'Class'
#    type = diagram.ClassItem
#    subject_type = UML.Class
#
#register_action(ClassPlacementAction)

#class MetaClassPlacementAction(ClassPlacementAction):
#    id = 'InsertMetaClass'
#    label = '_Metaclass'
#
#register_action(MetaClassPlacementAction)


class InterfacePlacementTool(gaphas.tool.PlacementTool):
    """The Interface placement tool creates an InterfaceItem and a
    DependencyItem (for the Implementation relationship) on the diagram.
    """

    def __init__(self, window, action_id):
        gaphas.tool.PlacementTool.__init__(self, None)
        self._window = window
        self.action_id = action_id
        self.handle_tool = diacanvas.view.HandleTool()

    def do_button_press_event(self, view, event):
        factory = resource(UML.ElementFactory)
        diag = self._window.get_current_diagram()
        iface = factory.create(UML.Interface)
        iface.package = diag.namespace
        iface_item = diag.create(diagram.InterfaceItem)
        iface_item.set_property('parent', view.canvas.root)
        iface_item.subject = iface
        impl_item = diag.create(diagram.DependencyItem)
        impl_item.set_dependency_type(UML.Implementation)
        impl_item.set_property('parent', view.canvas.root)

        wx, wy = view.window_to_world(event.x, event.y)
        ix, iy = iface_item.affine_point_w2i(wx, wy)
        iface_item.move(ix, iy)
        
        ix += iface_item.RADIUS * 2
        iy += iface_item.RADIUS
        impl_item.move(ix, iy)
        
        # Select the new items:
        view.unselect_all()
        view.select(view.find_view_item(iface_item))
        view.focus(view.find_view_item(impl_item))

        # Attach the head handle to the interface item:
        first = impl_item.handles[0]
        iface_item.connect_handle(first)

        # Grab the last handle with the mouse cursor
        last = impl_item.handles[-1]
        last.set_pos_i(20,0)
        self.handle_tool.set_grabbed_handle(last)
        return True

    def do_button_release_event(self, view, event):
        view.set_tool(None)
        return self.handle_tool.button_release(view, event)

    def do_motion_notify_event(self, view, event):
        return self.handle_tool.motion_notify(view, event)

#import gobject
#gobject.type_register(InterfacePlacementTool)

#class InterfacePlacementAction(NamespacePlacementAction):
#    id = 'InsertInterface'
#    label = '_Interface'
#    tooltip = 'Create a new interface item'
#    stock_id = 'gaphor-interface'
#    name = 'Interface'
#    type = diagram.InterfaceItem
#    subject_type = UML.Interface
#
#    def _execute(self):
#        tool = InterfacePlacementTool(self._window, self.id)
#        self._window.get_current_diagram_view().set_tool(tool)
#        self._window.set_message('Create new %s' % self.name)
#
#register_action(InterfacePlacementAction)


#class StereotypePlacementAction(NamespacePlacementAction):
#    id = 'InsertStereotype'
#    label = '_Stereotype'
#    tooltip = 'Create a new stereotype item'
#    stock_id = 'gaphor-stereotype'
#    name = 'Stereotype'
#    type = diagram.ClassItem
#    subject_type = UML.Stereotype
#
#register_action(StereotypePlacementAction)


#class ProfilePlacementAction(NamespacePlacementAction):
#    id = 'InsertProfile'
#    label = '_Profile'
#    tooltip = 'Create a new profile'
#    stock_id = 'gaphor-profile'
#    name = 'Profile'
#    type = diagram.PackageItem
#    subject_type = UML.Profile
#
#register_action(ProfilePlacementAction)


#class PackagePlacementAction(NamespacePlacementAction):
#    id = 'InsertPackage'
#    label = '_Package'
#    tooltip = 'Create a new package item'
#    stock_id = 'gaphor-package'
#    name = 'Package'
#    type = diagram.PackageItem
#    subject_type = UML.Package
#
#register_action(PackagePlacementAction)


#class InitialNodePlacementAction(PlacementAction):
#    id = 'InsertInitialNode'
#    label = 'Initial Node'
#    tooltip = 'Create a new initial node'
#    stock_id = 'gaphor-initial-node'
#    name = 'InitialNode'
#    type = diagram.InitialNodeItem
#    subject_type = UML.InitialNode
#
#register_action(InitialNodePlacementAction)


#class ActivityFinalNodePlacementAction(PlacementAction):
#    id = 'InsertActivityFinalNode'
#    label = 'Activity Final Node'
#    tooltip = 'Create a new activity final node'
#    stock_id = 'gaphor-activity-final-node'
#    name = 'ActivityFinalNode'
#    type = diagram.ActivityFinalNodeItem
#    subject_type = UML.ActivityFinalNode
#
#register_action(ActivityFinalNodePlacementAction)


#class FlowFinalNodePlacementAction(PlacementAction):
#    id = 'InsertFlowFinalNode'
#    label = 'Flow Final Node'
#    tooltip = 'Create a new flow final node'
#    stock_id = 'gaphor-flow-final-node'
#    name = 'FlowFinalNode'
#    type = diagram.FlowFinalNodeItem
#    subject_type = UML.FlowFinalNode
#
#register_action(FlowFinalNodePlacementAction)


#class DecisionNodePlacementAction(PlacementAction):
#    id = 'InsertDecisionNode'
#    label = 'Decision/Merge Node'
#    tooltip = 'Create a new decision/merge node'
#    stock_id = 'gaphor-decision-node'
#    name = 'DecisionNode'
#    type = diagram.DecisionNodeItem
#    subject_type = UML.DecisionNode
#
#register_action(DecisionNodePlacementAction)


#class ForkNodePlacementAction(PlacementAction):
#    id = 'InsertForkNode'
#    label = 'Fork/Join Node'
#    tooltip = 'Create a new fork/join node'
#    stock_id = 'gaphor-fork-node'
#    name = 'ForkNode'
#    type = diagram.ForkNodeItem
#    subject_type = UML.ForkNode
#
#register_action(ForkNodePlacementAction)


#class ActionPlacementAction(NamespacePlacementAction):
#    id = 'InsertAction'
#    label = 'Action'
#    tooltip = 'Create a new action'
#    stock_id = 'gaphor-action'
#    name = 'Action'
#    type = diagram.ActionItem
#    subject_type = UML.Action
#
#register_action(ActionPlacementAction)


#class ObjectNodePlacementAction(NamespacePlacementAction):
#    id = 'InsertObjectNode'
#    label = 'Object Node'
#    tooltip = 'Create a new object node'
#    stock_id = 'gaphor-object-node'
#    name = 'Object'
#    type = diagram.ObjectNodeItem
#    subject_type = UML.ObjectNode
#
#register_action(ObjectNodePlacementAction)


class CommentPlacementAction(PlacementAction):
    id = 'InsertComment'
    label = 'C_omment'
    tooltip = 'Create a new comment item'
    stock_id = 'gaphor-comment'
    name = 'Comment'
    type = diagram.CommentItem
    subject_type = UML.Comment

register_action(CommentPlacementAction)


class CommentLinePlacementAction(PlacementAction):
    id = 'InsertCommentLine'
    label = 'Comment _line'
    tooltip = 'Create a new comment line'
    stock_id = 'gaphor-comment-line'
    name = 'Comment line'
    type = diagram.CommentLineItem

register_action(CommentLinePlacementAction)


#class AssociationPlacementAction(PlacementAction):
#    id = 'InsertAssociation'
#    label = '_Association'
#    tooltip = 'Create a new association line'
#    stock_id = 'gaphor-association'
#    name = 'Association'
#    type = diagram.AssociationItem
#
#register_action(AssociationPlacementAction)


#class UseCaseAssociationPlacementAction(AssociationPlacementAction):
#    id = 'InsertUseCaseAssociation'
#
#register_action(UseCaseAssociationPlacementAction)


#class ExtensionPlacementAction(PlacementAction):
#    id = 'InsertExtension'
#    label = '_Extension'
#    tooltip = 'Create a new extension line'
#    stock_id = 'gaphor-extension'
#    name = 'Extension'
#    type = diagram.ExtensionItem
#
#register_action(ExtensionPlacementAction)


#class DependencyPlacementAction(PlacementAction):
#    id = 'InsertDependency'
#    label = '_Dependency'
#    tooltip = 'Create a new dependency'
#    stock_id = 'gaphor-dependency'
#    name = 'Dependency'
#    type = diagram.DependencyItem
#
#register_action(DependencyPlacementAction)


#class GeneralizationPlacementAction(PlacementAction):
#    id = 'InsertGeneralization'
#    label = '_Generalization'
#    tooltip = 'Create a new generalization'
#    stock_id = 'gaphor-generalization'
#    name = 'Generalization'
#    type = diagram.GeneralizationItem
#
#register_action(GeneralizationPlacementAction)


#class ImplementationPlacementAction(PlacementAction):
#    id = 'InsertImplementation'
#    label = '_Implementation'
#    tooltip = 'Create a new implementation'
#    stock_id = 'gaphor-implementation'
#    name = 'Implementation'
#    type = diagram.ImplementationItem
#
#register_action(ImplementationPlacementAction)


#class FlowPlacementAction(PlacementAction):
#    id = 'InsertFlow'
#    label = 'Control/Object _Flow'
#    tooltip = 'Create a new control/object flow'
#    stock_id = 'gaphor-control-flow'
#    name = 'Flow'
#    type = diagram.FlowItem
#
#register_action(FlowPlacementAction)


#class ComponentPlacementAction(NamespacePlacementAction):
#    id = 'InsertComponent'
#    label = '_Component'
#    tooltip = 'Create a new component item'
#    stock_id = 'gaphor-component'
#    name = 'Component'
#    type = diagram.ComponentItem
#    subject_type = UML.Component
#
#register_action(ComponentPlacementAction)


#class ConnectorPlacementAction(PlacementAction):
#    id = 'InsertConnector'
#    label = '_Connector'
#    tooltip = 'Create a new connector item'
#    stock_id = 'gaphor-connector'
#    name = 'Connector'
#    type = diagram.ConnectorItem
#
#register_action(ConnectorPlacementAction)


#class AssemblyConnectorPlacementAction(PlacementAction):
#    id = 'InsertAssemblyConnector'
#    label = 'Assembly Connector'
#    tooltip = 'Create a new assembly connector item'
#    stock_id = 'gaphor-assembly-connector'
#    name = 'AssemblyConnector'
#    type = diagram.AssemblyConnectorItem
#    subject_type = UML.Connector
#
#register_action(AssemblyConnectorPlacementAction)


#class ArtifactPlacementAction(NamespacePlacementAction):
#    id = 'InsertArtifact'
#    label = '_Artifact'
#    tooltip = 'Create a new artifact item'
#    stock_id = 'gaphor-artifact'
#    name = 'Artifact'
#    type = diagram.ArtifactItem
#    subject_type = UML.Artifact
#
#register_action(ArtifactPlacementAction)


#class NodePlacementAction(NamespacePlacementAction):
#    id = 'InsertNode'
#    label = '_Node'
#    tooltip = 'Create a new node item'
#    stock_id = 'gaphor-node'
#    name = 'Node'
#    type = diagram.NodeItem
#    subject_type = UML.Node
#
#register_action(NodePlacementAction)

#class InteractionPlacementAction(NamespacePlacementAction):
#    id = 'InsertInteraction'
#    label = '_Interaction'
#    tooltip = 'Create a new interaction item'
#    stock_id = 'gaphor-interaction'
#    name = 'Interaction'
#    type = diagram.InteractionItem
#    subject_type = UML.Interaction
#
#register_action(InteractionPlacementAction)

#class LifelinePlacementAction(PlacementAction):
#    id = 'InsertLifeline'
#    label = '_Lifeline'
#    tooltip = 'Create a new lifeline item'
#    stock_id = 'gaphor-lifeline'
#    name = 'Lifeline'
#    type = diagram.LifelineItem
#    subject_type = UML.Lifeline
#    __index = 1
#
#    def item_factory(self):
#        """Create a new instance of the item and return it."""
#        item = PlacementAction.item_factory(self)
#        #log.debug('Setting namespace for new item %s: %s' % (item, self._window.get_current_diagram().namespace))
#        #item.subject.interaction = self._window.get_current_diagram().namespace
#        item.subject.name = '%s%d' % (self.name, self.__index)
#        self.__index += 1
#        return item
#
#register_action(LifelinePlacementAction)


#class MessagePlacementAction(PlacementAction):
#    id = 'InsertMessage'
#    label = '_Message'
#    tooltip = 'Create a new message line'
#    stock_id = 'gaphor-message'
#    name = 'Message'
#    type = diagram.MessageItem
#
#register_action(MessagePlacementAction)


