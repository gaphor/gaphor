# vim:sw=4
"""Menu actions that create diagram items.

This module is initialized from gaphor.ui.diagramwindow
"""
import diacanvas
import gaphor
import gaphor.UML as UML
import gaphor.diagram as diagram
from gaphor.misc.action import Action, CheckAction, RadioAction
from gaphor.misc.action import register_action as _register_action
from gaphor.misc.action import action_dependencies as _action_dependencies
from gaphor import resource

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


class ResetToolAfterCreateAction(CheckAction):
    id = 'ResetToolAfterCreate'
    label = 'Reset _tool'
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
    __index = 1

    def item_factory(self):
        """Create a new instance of the item and return it."""
        item = PlacementAction.item_factory(self)
        #log.debug('Setting namespace for new item %s: %s' % (item, self._window.get_current_diagram().namespace))
        item.subject.package = self._window.get_current_diagram().namespace
        item.subject.name = '%s%d' % (self.name, self.__index)
        self.__index += 1
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


class IncludePlacementAction(PlacementAction):
    id = 'InsertInclude'
    label = '_Include'
    tooltip = 'Create a new Include'
    stock_id = 'gaphor-include'
    name = 'Include'
    type = diagram.IncludeItem

register_action(IncludePlacementAction)


class ExtendPlacementAction(PlacementAction):
    id = 'InsertExtend'
    label = '_Extend'
    tooltip = 'Create a new Extend'
    stock_id = 'gaphor-extend'
    name = 'Extend'
    type = diagram.ExtendItem

register_action(ExtendPlacementAction)


class ClassPlacementAction(NamespacePlacementAction):
    id = 'InsertClass'
    label = '_Class'
    tooltip = 'Create a new Class item'
    stock_id = 'gaphor-class'
    name = 'Class'
    type = diagram.ClassItem
    subject_type = UML.Class

register_action(ClassPlacementAction)

class MetaClassPlacementAction(ClassPlacementAction):
    id = 'InsertMetaClass'
    label = '_Metaclass'

register_action(MetaClassPlacementAction)


class InterfacePlacementTool(diacanvas.PlacementTool):
    """The Interface placement tool creates an InterfaceItem and a
    DependencyItem (for the Implementation relationship) on the diagram.
    """

    def __init__(self, window, action_id):
        diacanvas.PlacementTool.__init__(self, None)
        self._window = window
        self.action_id = action_id
        self.handle_tool = diacanvas.view.HandleTool()

    def do_button_press_event(self, view, event):
        factory = gaphor.resource('ElementFactory')
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

import gobject
gobject.type_register(InterfacePlacementTool)

class InterfacePlacementAction(NamespacePlacementAction):
    id = 'InsertInterface'
    label = '_Interface'
    tooltip = 'Create a new Interface item'
    stock_id = 'gaphor-interface'
    name = 'Interface'
    type = diagram.InterfaceItem
    subject_type = UML.Interface

    def _execute(self):
        tool = InterfacePlacementTool(self._window, self.id)
        self._window.get_current_diagram_view().set_tool(tool)
        self._window.set_message('Create new %s' % self.name)

register_action(InterfacePlacementAction)


class StereotypePlacementAction(NamespacePlacementAction):
    id = 'InsertStereotype'
    label = '_Stereotype'
    tooltip = 'Create a new Stereotype item'
    stock_id = 'gaphor-stereotype'
    name = 'Stereotype'
    type = diagram.ClassItem
    subject_type = UML.Stereotype

register_action(StereotypePlacementAction)


class ProfilePlacementAction(NamespacePlacementAction):
    id = 'InsertProfile'
    label = '_Profile'
    tooltip = 'Create a new Profile'
    stock_id = 'gaphor-profile'
    name = 'Profile'
    type = diagram.PackageItem
    subject_type = UML.Profile

register_action(ProfilePlacementAction)


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


class UseCaseAssociationPlacementAction(AssociationPlacementAction):
    id = 'InsertUseCaseAssociation'

register_action(UseCaseAssociationPlacementAction)


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


class ImplementationPlacementAction(PlacementAction):
    id = 'InsertImplementation'
    label = '_Implementation'
    tooltip = 'Create a new Implementation'
    stock_id = 'gaphor-implementation'
    name = 'Implementation'
    type = diagram.ImplementationItem

register_action(ImplementationPlacementAction)


class FlowPlacementAction(PlacementAction):
    id = 'InsertFlow'
    label = '_Flow'
    tooltip = 'Create a Flow'
    stock_id = 'gaphor-control-flow'
    name = 'Flow'
    type = diagram.FlowItem

register_action(FlowPlacementAction)

class ComponentPlacementAction(NamespacePlacementAction):
    id = 'InsertComponent'
    label = '_Component'
    tooltip = 'Create a new Component item'
    stock_id = 'gaphor-component'
    name = 'Component'
    type = diagram.ComponentItem
    subject_type = UML.Component

register_action(ComponentPlacementAction)

class ArtifactPlacementAction(NamespacePlacementAction):
    id = 'InsertArtifact'
    label = '_Artifact'
    tooltip = 'Create a new Artifact item'
    stock_id = 'gaphor-artifact'
    name = 'Artifact'
    type = diagram.ArtifactItem
    subject_type = UML.Artifact

register_action(ArtifactPlacementAction)

class NodePlacementAction(NamespacePlacementAction):
    id = 'InsertNode'
    label = '_Node'
    tooltip = 'Create a new Node item'
    stock_id = 'gaphor-node'
    name = 'Node'
    type = diagram.NodeItem
    subject_type = UML.Node

register_action(NodePlacementAction)

