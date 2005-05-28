# vim:sw=4:et
"""
Commands related to the Diagram (DiaCanvas)
"""

from __future__ import generators

import diacanvas

from gaphor import GaphorError, resource
from gaphor import UML
from gaphor.undomanager import UndoTransactionAspect, weave_method
from gaphor.misc.action import Action, CheckAction, RadioAction, ObjectAction
from gaphor.misc.action import register_action

from gaphor.diagram.klass import ClassItem
from gaphor.diagram.package import PackageItem
from gaphor.diagram.component import ComponentItem
from gaphor.diagram.attribute import AttributeItem
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.operation import OperationItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.interface import InterfaceItem
from gaphor.diagram.association import AssociationItem, AssociationEnd
from gaphor.diagram import ClassifierItem, ImplementationItem, \
     GeneralizationItem, DependencyItem


class NoFocusItemError(GaphorError):
    pass


def get_parent_focus_item(window):
    """Get the outer most focus item (the obe that's not a composite)."""
    view = window.get_current_diagram_view()
    if view:
        fi = view.focus_item
        if fi:
            item = fi.item
            while (item.flags & diacanvas.COMPOSITE) != 0:
                item = item.parent
            return item
    raise NoFocusItemError, 'No item has focus.'

def get_pointer(view):
    x, y = view.get_pointer()
    x = x + view.get_hadjustment().value
    y = y + view.get_vadjustment().value
    return x, y

class ItemNewSubjectAction(Action):
    id = 'ItemNewSubject'

    def init(self, window):
        self._window = window

    def execute(self):
        self._window.execute_action('ItemFocus')

register_action(ItemNewSubjectAction)

class EditItemAction(Action):
    id = 'EditItem'
    label = 'Edit'
    tooltip='Edit'

    def init(self, window):
        self._window = window

    def execute(self):
        # Stay backwards compatible:
        view = self._window.get_current_diagram_view()
        wx, wy = view.window_to_world(*get_pointer(view))
        #log.debug('focus item %s on point (%d, %d) -> (%d, %d)' % (view.focus_item.item, x, y, wx, wy))
        view.start_editing(view.focus_item, wx, wy)

register_action(EditItemAction, 'ItemFocus')


class RenameItemAction(EditItemAction):
    id = 'RenameItem'
    label = '_Rename'
    tooltip = 'Rename selected item'

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            self.sensitive = False
        else:
            if isinstance(item, NamedItem):
                self.sensitive = True

register_action(RenameItemAction, 'ItemFocus')


class AbstractClassAction(CheckAction):
    id = 'AbstractClass'
    label = 'Abstract Class'
    tooltip='Abstract class'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ClassItem):
                self.active = item.subject and item.subject.isAbstract

    def execute(self):
        item = get_parent_focus_item(self._window)
        if item and item.subject:
            item.subject.isAbstract = self.active

weave_method(AbstractClassAction.execute, UndoTransactionAspect)
register_action(AbstractClassAction, 'ItemFocus')


class AbstractOperationAction(CheckAction):
    id = 'AbstractOperation'
    label = 'Abstract Operation'
    tooltip='Abstract operation'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            get_parent_focus_item(self._window)
            item = self._window.get_current_diagram_view() \
                .focus_item.item
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, OperationItem):
                self.active = item.subject and item.subject.isAbstract

    def execute(self):
        item = self._window.get_current_diagram_view() \
            .focus_item.item
        if item and item.subject:
            item.subject.isAbstract = self.active

weave_method(AbstractOperationAction.execute, UndoTransactionAspect)
register_action(AbstractOperationAction, 'ItemFocus')


# NOTE: attributes and operations can now only be created on classes,
#       actors and use-cases are also classifiers, but we can't add 
#       attrs and opers via the UI right now.

class CreateAttributeAction(Action):
    id = 'CreateAttribute'
    label = 'New _Attribute'
    tooltip = 'Create a new attribute'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ClassItem):
                self.sensitive = item.get_property('show-attributes')

    def execute(self):
        view = self._window.get_current_diagram_view()
        focus_item = get_parent_focus_item(self._window)
        subject = focus_item.subject
        assert isinstance(subject, (UML.Class, UML.Interface))
        elemfact = resource(UML.ElementFactory)
        
        attribute = elemfact.create(UML.Property)
        attribute.parse('new')
        subject.ownedAttribute = attribute

        # Select this item for editing
        presentation = attribute.presentation
        focus_item.update_now()

        wx, wy = view.window_to_world(*get_pointer(view))
        for f in focus_item.groupable_iter():
            if f in presentation:
                vf = view.find_view_item(f)
                view.start_editing(vf, wx, wy)
                break

weave_method(CreateAttributeAction.execute, UndoTransactionAspect)
register_action(CreateAttributeAction, 'ShowAttributes', 'ItemFocus')


class CreateOperationAction(Action):
    id = 'CreateOperation'
    label = 'New _Operation'
    tooltip = 'Create a new operation'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ClassItem):
                self.sensitive = item.get_property('show-operations')

    def execute(self):
        view = self._window.get_current_diagram_view()
        focus_item = get_parent_focus_item(self._window)
        subject = focus_item.subject
        assert isinstance(subject, UML.Classifier)
        elemfact = resource(UML.ElementFactory)

        operation = elemfact.create(UML.Operation)
        operation.parse('new()')
        subject.ownedOperation = operation
        # Select this item for editing
        presentation = operation.presentation
        focus_item.update_now()

        wx, wy = view.window_to_world(*get_pointer(view))
        for f in focus_item.groupable_iter():
            if f in presentation:
                vf = view.find_view_item(f)
                view.start_editing(vf, wx, wy)
                break

weave_method(CreateOperationAction.execute, UndoTransactionAspect)
register_action(CreateOperationAction, 'ShowOperations', 'ItemFocus')


class DeleteFeatureAction(Action):

    def init(self, window):
        self._window = window

    def execute(self):
        #subject = get_parent_focus_item(self._window).subject
        item = self._window.get_current_diagram_view().focus_item.item
        #assert isinstance(subject, (UML.Property, UML.Operation))
        item.subject.unlink()


class DeleteAttributeAction(DeleteFeatureAction):
    id = 'DeleteAttribute'
    label = 'Delete A_ttribute'
    tooltip='Delete the selected attribute'

weave_method(DeleteAttributeAction.execute, UndoTransactionAspect)
register_action(DeleteAttributeAction, 'ShowAttributes', 'CreateAttribute', 'ItemFocus')


class DeleteOperationAction(DeleteFeatureAction):
    id = 'DeleteOperation'
    label = 'Delete O_peration'
    tooltip = 'Delete the selected operation'

weave_method(DeleteOperationAction.execute, UndoTransactionAspect)
register_action(DeleteOperationAction, 'ShowOperations', 'CreateOperation', 'ItemFocus')


class ShowAttributesAction(CheckAction):
    id = 'ShowAttributes'
    label = 'Show Attributes'
    tooltip='show attribute compartment'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ClassItem):
                self.active = item.get_property('show-attributes')

    def execute(self):
        item = get_parent_focus_item(self._window)
        item.set_property('show-attributes', self.active)

weave_method(DeleteOperationAction.execute, UndoTransactionAspect)
register_action(ShowAttributesAction, 'ItemFocus')


class ShowOperationsAction(CheckAction):
    id = 'ShowOperations'
    label = 'Show Operations'
    tooltip='Show attribute compartment'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ClassItem):
                self.active = item.get_property('show-operations')

    def execute(self):
        item = get_parent_focus_item(self._window)
        item.set_property('show-operations', self.active)

weave_method(ShowOperationsAction.execute, UndoTransactionAspect)
register_action(ShowOperationsAction, 'ItemFocus')

#
# Lines:
#

class SegmentAction(Action):
    """Base class for add and delete line segment."""

    def init(self, window):
        self._window = window

    def get_item_and_segment(self):
        fi = get_parent_focus_item(self._window)
        view = self._window.get_current_diagram_view()
        assert isinstance(fi, diacanvas.CanvasLine)
        #x = view.event()
        #print 'event =', event
        wx, wy = view.window_to_world(*get_pointer(view))
        x, y = fi.affine_point_w2i(wx, wy)
        segment = fi.get_closest_segment(x, y)
        return fi, segment


class AddSegmentAction(SegmentAction):
    id = 'AddSegment'
    label = 'Add _Segment'
    tooltip='Add a segment to the line'

    def execute(self):
        item, segment = self.get_item_and_segment()
        if item:
            item.set_property('add_segment', segment)
            
weave_method(AddSegmentAction.execute, UndoTransactionAspect)
register_action(AddSegmentAction, 'ItemFocus')


class DeleteSegmentAction(SegmentAction):
    id = 'DeleteSegment'
    label = 'Delete _Segment'
    tooltip = 'Delete the segment from the line'

    def update(self):
        try:
            fi = get_parent_focus_item(self._window)
            if fi and isinstance(fi, diacanvas.CanvasLine):
                self.sensitive = len(fi.handles) > 2
        except NoFocusItemError:
            pass

    def execute(self):
        item, segment = self.get_item_and_segment()
        if item:
            item.set_property('del_segment', segment)
            
weave_method(DeleteSegmentAction.execute, UndoTransactionAspect)
register_action(DeleteSegmentAction, 'ItemFocus', 'AddSegment')


class OrthogonalAction(CheckAction):
    id = 'Orthogonal'
    label = 'Orthogonal'
    tooltip = 'Set the line to orthogonal'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            fi = get_parent_focus_item(self._window)
            if fi and isinstance(fi, diacanvas.CanvasLine):
                self.active = fi.get_property('orthogonal')
        except NoFocusItemError:
            pass

    def execute(self):
        fi = get_parent_focus_item(self._window)
        assert isinstance(fi, diacanvas.CanvasLine)
        if self.active and len(fi.handles) < 3:
            fi.set_property('add_segment', 0)
        fi.set_property('orthogonal', self.active)

weave_method(OrthogonalAction.execute, UndoTransactionAspect)
register_action(OrthogonalAction, 'ItemFocus', 'AddSegment', 'DeleteSegment')


class OrthogonalAlignmentAction(CheckAction):
    id = 'OrthogonalAlignment'
    label = 'Switched Alignment'
    tooltip = 'Set the line to orthogonal'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            fi = get_parent_focus_item(self._window)
            if fi and isinstance(fi, diacanvas.CanvasLine):
                self.sensitive = fi.get_property('orthogonal')
                self.active = fi.get_property('horizontal')
        except NoFocusItemError:
            pass

    def execute(self):
        fi = get_parent_focus_item(self._window)
        assert isinstance(fi, diacanvas.CanvasLine)
        fi.set_property('horizontal', self.active)

weave_method(OrthogonalAlignmentAction.execute, UndoTransactionAspect)
register_action(OrthogonalAlignmentAction, 'ItemFocus', 'Orthogonal')


#
# Association submenu
#

class AssociationShowDirectionAction(CheckAction):
    id = 'AssociationShowDirection'
    label = 'Show Direction'
    tooltip='Show direction arrow'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            if isinstance(item, AssociationItem):
                self.active = item.get_property('show-direction')
        except NoFocusItemError:
            pass

    def execute(self):
        fi = get_parent_focus_item(self._window)
        assert isinstance(fi, AssociationItem)
        fi.set_property('show-direction', self.active)

weave_method(AssociationShowDirectionAction.execute, UndoTransactionAspect)
register_action(AssociationShowDirectionAction, 'ItemFocus')


class AssociationInvertDirectionAction(Action):
    id = 'AssociationInvertDirection'
    label = 'Invert Direction'
    tooltip='Invert direction arrow'

    def init(self, window):
        self._window = window

    def execute(self):
        fi = get_parent_focus_item(self._window)
        assert isinstance(fi, AssociationItem)
        fi.invert_direction()

weave_method(AssociationInvertDirectionAction.execute, UndoTransactionAspect)
register_action(AssociationInvertDirectionAction, 'ItemFocus')


class NavigableAction(RadioAction):
    end_name=''
    def init(self, window):
        self._window = window

    def get_association_end(self):
        return get_parent_focus_item(self._window).get_property(self.end_name)

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            if isinstance(item, AssociationItem):
                end = item.get_property(self.end_name)
                if end.subject:
                    self.active = (end.get_navigability() == self.navigable)
        except NoFocusItemError:
            pass

    def execute(self):
        item = self.get_association_end()
        assert item.subject
        assert isinstance(item.subject, UML.Property)
        item.set_navigable(self.navigable)

weave_method(NavigableAction.execute, UndoTransactionAspect)


class HeadNavigableAction(NavigableAction):
    id = 'Head_isNavigable'
    label = 'Navigable'
    end_name = 'head'
    navigable = True

register_action(HeadNavigableAction, 'ItemFocus')


class HeadNotNavigableAction(NavigableAction):
    id = 'Head_isNotNavigable'
    label = 'Non-Navigable'
    end_name = 'head'
    navigable = False

register_action(HeadNotNavigableAction, 'ItemFocus')


class HeadUnknownNavigationAction(NavigableAction):
    id = 'Head_unknownNavigation'
    label = 'Unknown'
    end_name = 'head'
    navigable = None

register_action(HeadUnknownNavigationAction, 'ItemFocus')


class TailNavigableAction(NavigableAction):
    id = 'Tail_isNavigable'
    label = 'Navigable'
    end_name = 'tail'
    navigable = True

register_action(TailNavigableAction, 'ItemFocus')


class TailNotNavigableAction(NavigableAction):
    id = 'Tail_isNotNavigable'
    label = 'Non-Navigable'
    end_name = 'tail'
    navigable = False

register_action(TailNotNavigableAction, 'ItemFocus')


class TailUnknownNavigationAction(NavigableAction):
    id = 'Tail_unknownNavigation'
    label = 'Unknown'
    end_name = 'tail'
    navigable = None

register_action(TailUnknownNavigationAction, 'ItemFocus')


class AggregationAction(RadioAction):

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            if isinstance(item, AssociationItem):
                end = item.get_property(self.end_name)
                if end.subject:
                    self.active = (end.subject.aggregation == self.aggregation)
        except NoFocusItemError:
            pass

    def execute(self):
        if self.active:
            subject = get_parent_focus_item(self._window).get_property(self.end_name).subject
            assert isinstance(subject, UML.Property)
            subject.aggregation = self.aggregation

weave_method(AggregationAction.execute, UndoTransactionAspect)

class HeadNoneAction(AggregationAction):
    id = 'Head_AggregationNone'
    label = 'None'
    group = 'head_aggregation'
    end_name = 'head'
    aggregation = 'none'

register_action(HeadNoneAction, 'ItemFocus')


class HeadSharedAction(AggregationAction):
    id = 'Head_AggregationShared'
    label = 'Shared'
    group = 'head_aggregation'
    end_name = 'head'
    aggregation = 'shared'

register_action(HeadSharedAction, 'ItemFocus')


class HeadCompositeAction(AggregationAction):
    id = 'Head_AggregationComposite'
    label = 'Composite'
    group = 'head_aggregation'
    end_name = 'head'
    aggregation = 'composite'

register_action(HeadCompositeAction, 'ItemFocus')


class TailNoneAction(AggregationAction):
    id = 'Tail_AggregationNone'
    label = 'None'
    group = 'tail_aggregation'
    end_name = 'tail'
    aggregation = 'none'

register_action(TailNoneAction, 'ItemFocus')


class TailSharedAction(AggregationAction):
    id = 'Tail_AggregationShared'
    label = 'Shared'
    group = 'tail_aggregation'
    end_name = 'tail'
    aggregation = 'shared'

register_action(TailSharedAction, 'ItemFocus')


class TailCompositeAction(AggregationAction):
    id = 'Tail_AggregationComposite'
    label = 'Composite'
    group = 'tail_aggregation'
    end_name = 'tail'
    aggregation = 'composite'

register_action(TailCompositeAction, 'ItemFocus')


class AssociationEndRenameNameAction(Action):
    id = 'AssociationEndRenameName'
    label = '_Rename'
    tooltip = 'Rename selected item'

    def init(self, window):
        self._window = window

    def update(self):
        view = self._window.get_current_diagram_view()
        if not view: return
        fi = view.focus_item
        if not fi:
            self.sensitive = False
        else:
            if isinstance(fi.item, AssociationEnd):
                self.sensitive = True

    def execute(self):
        item = self._window.get_current_diagram_view().focus_item.item
        if item.subject:
            item.edit_name()

register_action(AssociationEndRenameNameAction, 'ItemFocus')


class AssociationEndRenameMultAction(Action):
    id = 'AssociationEndRenameMult'
    label = '_Rename'
    tooltip = 'Rename selected item'

    def init(self, window):
        self._window = window

    def update(self):
        view = self._window.get_current_diagram_view()
        if not view: return
        fi = view.focus_item
        if not fi:
            self.sensitive = False
        else:
            if isinstance(fi.item, AssociationEnd):
                self.sensitive = True

    def execute(self):
        item = self._window.get_current_diagram_view().focus_item.item
        if item.subject:
            item.edit_mult()

register_action(AssociationEndRenameMultAction, 'ItemFocus')


class DependencyTypeAction(RadioAction):
    id = 'DependencyType'
    label = 'Automatic'
    group = 'dependency_type'
    dependency_type = None

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            if isinstance(item, DependencyItem):
                self.active = (item.get_dependency_type() == self.dependency_type)
        except NoFocusItemError:
            pass

    def execute(self):
        if self.active:
            item = get_parent_focus_item(self._window)
            item.set_dependency_type(self.dependency_type)
            #item.auto_dependency = False
            self._window.get_action_pool().execute('AutoDependency', active=False)

weave_method(DependencyTypeAction.execute, UndoTransactionAspect)
        

class DependencyTypeDependencyAction(DependencyTypeAction):
    id = 'DependencyTypeDependency'
    label = 'Dependency'
    group = 'dependency_type'
    dependency_type = UML.Dependency

register_action(DependencyTypeDependencyAction, 'ItemFocus')


class DependencyTypeUsageAction(DependencyTypeAction):
    id = 'DependencyTypeUsage'
    label = 'Usage'
    group = 'dependency_type'
    dependency_type = UML.Usage

register_action(DependencyTypeUsageAction, 'ItemFocus')


class DependencyTypeRealizationAction(DependencyTypeAction):
    id = 'DependencyTypeRealization'
    label = 'Realization'
    group = 'dependency_type'
    dependency_type = UML.Realization

register_action(DependencyTypeRealizationAction, 'ItemFocus')


class DependencyTypeImplementationAction(DependencyTypeAction):
    id = 'DependencyTypeImplementation'
    label = 'Implementation'
    group = 'dependency_type'
    dependency_type = UML.Implementation

register_action(DependencyTypeImplementationAction, 'ItemFocus')

class AutoDependencyAction(CheckAction):
    id = 'AutoDependency'
    label = 'Automatic'
    tooltip = 'Automatically determine the dependency type'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, DependencyItem):
                self.active = item.auto_dependency

    def execute(self):
        item = get_parent_focus_item(self._window)
        item.auto_dependency = self.active

weave_method(AutoDependencyAction.execute, UndoTransactionAspect)
register_action(AutoDependencyAction, 'ItemFocus')


class IndirectlyInstantiatedComponentAction(CheckAction):
    id = 'IndirectlyInstantiated'
    label = 'Indirectly Instantiated'
    tooltip = 'Indirectly instantiated component'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, ComponentItem):
                self.active = item.subject and item.subject.isIndirectlyInstantiated

    def execute(self):
        item = get_parent_focus_item(self._window)
        item.subject.isIndirectlyInstantiated = self.active

weave_method(IndirectlyInstantiatedComponentAction.execute, UndoTransactionAspect)
register_action(IndirectlyInstantiatedComponentAction, 'ItemFocus')


class MoveAction(Action):
    """
    Move attribute/operation down or up on the list.
    """
    def _getItem(self):
        return self._window.get_current_diagram_view() \
            .focus_item.item

    def _getParent(self):
        return get_parent_focus_item(self._window)

    def _getElements(self, cls, item):
        if isinstance(item, AttributeItem):
            collection = cls.ownedAttribute
        elif isinstance(item, OperationItem):
            collection = cls.ownedOperation
        return collection

    def init(self, window):
        self._window = window

    def update(self):
        try:
            cls_item = self._getParent()
            item = self._getItem()
        except NoFocusItemError:
            pass
        else:
            if isinstance(item, (AttributeItem, OperationItem)):
                self.active = item.subject 
                self.sensitive = self._isSensitive(cls_item.subject, item)

    def execute(self):
        cls = self._getParent().subject
        item = self._getItem()

        log.debug('%s: %s.%s (%s)' \
            % (self.move_action, cls.name, item.subject.name, item.subject.__class__))

        # get method to move the element: moveUp or moveDown
        move = getattr(self._getElements(cls, item), self.move_action)
        move(item.subject)
        self._window.execute_action('ItemFocus')

weave_method(MoveAction.execute, UndoTransactionAspect)

class MoveUpAction(MoveAction):
    id = 'MoveUp'
    label = 'Move Up'
    tooltip = 'Move up'
    move_action = 'moveUp' # name of method to move the element

    def _isSensitive(self, cls, item):
        collection = self._getElements(cls, item)
        return len(collection) > 0 and collection[0] != item.subject

register_action(MoveUpAction, 'ItemFocus')
            

class MoveDownAction(MoveAction):
    id = 'MoveDown'
    label = 'Move Down'
    tooltip = 'Move down'
    move_action = 'moveDown' # name of method to move the element

    def _isSensitive(self, cls, item):
        collection = self._getElements(cls, item)
        return len(collection) > 0 and collection[-1] != item.subject

register_action(MoveDownAction, 'ItemFocus')


class FoldAction(Action):
    id = 'Fold'
    label = '_Fold'
    tooltip = 'Hide details'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            self.sensitive = isinstance(item, InterfaceItem)

    def execute(self):
        item = get_parent_focus_item(self._window)
        #log.debug('Action %s: %s' % (self.id, item.subject.name))

        item.set_property('drawing-style', InterfaceItem.DRAW_ICON)

weave_method(FoldAction.execute, UndoTransactionAspect)
register_action(FoldAction, 'ItemFocus')


class UnfoldAction(FoldAction):
    id = 'Unfold'
    label = '_Unfold'
    tooltip = 'View details'

    def execute(self):
        item = get_parent_focus_item(self._window)
        #log.debug('Action %s: %s' % (self.id, item.subject.name))

        item.set_property('drawing-style', InterfaceItem.DRAW_COMPARTMENT)
        # Make sure lines are updated properly:
        item.canvas.update_now()
        item.canvas.update_now()

weave_method(UnfoldAction.execute, UndoTransactionAspect)
register_action(UnfoldAction, 'ItemFocus')


class ApplyStereotypeAction(CheckAction, ObjectAction):

    def __init__(self, stereotype):
        Action.__init__(self)
        ObjectAction.__init__(self, id='ApplyStereotype' + str(stereotype.name),
                             label=str(stereotype.name))
        self.stereotype = stereotype

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            self.sensitive = isinstance(item, (ClassItem, PackageItem))
            if self.sensitive and item.subject:
                self.active = self.stereotype in item.subject.appliedStereotype
            else:
                self.active = False

    def execute(self):
        item = get_parent_focus_item(self._window)
        if self.active:
            item.subject.appliedStereotype = self.stereotype
        else:
            del item.subject.appliedStereotype[self.stereotype]

weave_method(ApplyStereotypeAction.execute, UndoTransactionAspect)


class CreateLinksAction(Action):
    """Create links (associations, generalizations, dependencies) from
    the selected diagram items to other items on the same diagram. Those
    links have to exist in the data layer of course.
    """
    id = 'CreateLinks'
    label = '_Create Links'
    tooltip = 'Make existing relationships between diagram items visible'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and len(diagram_tab.get_view().selected_items) > 0

    def connect_relationship(self, rel, head_item, tail_item):
        """Connect the lines, the the Item's connect handler figure out
        which model element should be used as subject.
        """
        def find_center(item):
            """Find the center point of the item, in world coordinates
            """
            x = item.width / 2.0
            y = item.height / 2.0
            return item.affine_point_i2w(x, y)

        center0 = find_center(head_item)
        center1 = find_center(tail_item)
        center = (center0[0] + center1[0]) / 2.0, (center0[1] + center1[1]) / 2.0
        rel.handles[0].set_pos_w(*center)
        rel.handles[-1].set_pos_w(*center)

        head_item.connect_handle(rel.handles[0])
        tail_item.connect_handle(rel.handles[-1])

    def create_missing_relationships(self, item, diagram, item_type):
        new_rel = diagram.create(item_type)
        for other_item in diagram.canvas.root.children:
            if not other_item.subject:
                continue

            try:
                while new_rel.find_relationship(item.subject, other_item.subject):
                    self.connect_relationship(new_rel, item, other_item)
                    #item.connect_handle(new_rel.handles[0])
                    #other_item.connect_handle(new_rel.handles[-1])
                    # Create a new item we want to connect
                    new_rel = diagram.create(item_type)
            except AttributeError:
                pass

            # Try the other way too:
            try:
                while new_rel.find_relationship(other_item.subject, item.subject):
                    self.connect_relationship(new_rel, other_item, item)
                    #other_item.connect_handle(new_rel.handles[0])
                    #item.connect_handle(new_rel.handles[-1])
                    # Create a new item we want to connect
                    new_rel = diagram.create(item_type)
            except AttributeError:
                pass

        # We always create one relationship to much. Remove it.
        new_rel.unlink()

    def execute(self):
        diagram_tab = self._window.get_current_diagram_tab()
        diagram = diagram_tab.get_diagram()
        for view_item in diagram_tab.get_view().selected_items:
            item = view_item.item
            if isinstance(item, ClassItem):
                self.create_missing_relationships(item, diagram,
                                                  AssociationItem)

            if isinstance(item, ClassifierItem):
                self.create_missing_relationships(item, diagram,
                                                  ImplementationItem)
                self.create_missing_relationships(item, diagram,
                                                  GeneralizationItem)

            self.create_missing_relationships(item, diagram,
                                              DependencyItem)

weave_method(CreateLinksAction.execute, UndoTransactionAspect)
register_action(CreateLinksAction, 'ItemFocus', 'ItemSelect')

