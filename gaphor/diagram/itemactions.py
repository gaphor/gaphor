# vim: sw=4:et
"""
Commands related to the Diagram (DiaCanvas)
"""

import diacanvas
import gaphor
import gaphor.diagram
import gaphor.UML as UML
from gaphor.undomanager import get_undo_manager
from gaphor.misc.action import Action, CheckAction, RadioAction, ObjectAction
from gaphor.misc.action import register_action

from klass import ClassItem
from component import ComponentItem
from attribute import AttributeItem
from dependency import DependencyItem
from operation import OperationItem
from nameditem import NamedItem
from interface import InterfaceItem
from association import AssociationEnd

class NoFocusItemError(gaphor.GaphorError):
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
        wx, wy = view.window_to_world(*view.get_pointer())
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
    label = 'Abstract class'
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
        get_undo_manager().begin_transaction()
        item.subject.isAbstract = self.active
        get_undo_manager().commit_transaction()

register_action(AbstractClassAction, 'ItemFocus')


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
        elemfact = gaphor.resource(UML.ElementFactory)
        
        get_undo_manager().begin_transaction()
        attribute = elemfact.create(UML.Property)
        attribute.parse('new')
        subject.ownedAttribute = attribute

        # Select this item for editing
        presentation = attribute.presentation
        focus_item.update_now()

        wx, wy = view.window_to_world(*view.get_pointer())
        for f in focus_item.groupable_iter():
            if f in presentation:
                vf = view.find_view_item(f)
                view.start_editing(vf, wx, wy)
                break
        get_undo_manager().commit_transaction()

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
        elemfact = gaphor.resource(UML.ElementFactory)

        get_undo_manager().begin_transaction()
        operation = elemfact.create(UML.Operation)
        operation.parse('new()')
        subject.ownedOperation = operation
        # Select this item for editing
        presentation = operation.presentation
        focus_item.update_now()

        wx, wy = view.window_to_world(*view.get_pointer())
        for f in focus_item.groupable_iter():
            if f in presentation:
                vf = view.find_view_item(f)
                view.start_editing(vf, wx, wy)
                break
        get_undo_manager().commit_transaction()

register_action(CreateOperationAction, 'ShowOperations', 'ItemFocus')


class DeleteFeatureAction(Action):

    def init(self, window):
        self._window = window

    def execute(self):
        #subject = get_parent_focus_item(self._window).subject
        item = self._window.get_current_diagram_view().focus_item.item
        #assert isinstance(subject, (UML.Property, UML.Operation))
        get_undo_manager().begin_transaction()
        item.subject.unlink()
        get_undo_manager().commit_transaction()


class DeleteAttributeAction(DeleteFeatureAction):
    id = 'DeleteAttribute'
    label = 'Delete A_ttribute'
    tooltip='Delete the selected attribute'

register_action(DeleteAttributeAction, 'ShowAttributes', 'CreateAttribute', 'ItemFocus')


class DeleteOperationAction(DeleteFeatureAction):
    id = 'DeleteOperation'
    label = 'Delete O_peration'
    tooltip = 'Delete the selected operation'

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
        get_undo_manager().begin_transaction()
        item.set_property('show-attributes', self.active)
        get_undo_manager().commit_transaction()

register_action(ShowAttributesAction, 'ItemFocus')


class ShowOperationsAction(CheckAction):
    id = 'ShowOperations'
    label = 'Show Operations'
    tooltip='show attribute compartment'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            from klass import ClassItem
            if isinstance(item, ClassItem):
                self.active = item.get_property('show-operations')

    def execute(self):
        item = get_parent_focus_item(self._window)
        get_undo_manager().begin_transaction()
        item.set_property('show-operations', self.active)
        get_undo_manager().commit_transaction()

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
        wx, wy = view.window_to_world(*view.get_pointer())
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
            get_undo_manager().begin_transaction()
            item.set_property('add_segment', segment)
            get_undo_manager().commit_transaction()
            
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
            get_undo_manager().begin_transaction()
            item.set_property('del_segment', segment)
            get_undo_manager().commit_transaction()
            
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
        get_undo_manager().begin_transaction()
        if self.active and len(fi.handles) < 3:
            fi.set_property('add_segment', 0)
        fi.set_property('orthogonal', self.active)
        get_undo_manager().commit_transaction()

register_action(OrthogonalAction, 'ItemFocus', 'AddSegment', 'DeleteSegment')


class OrthogonalAlignmentAction(CheckAction):
    id = 'OrthogonalAlignment'
    label = 'Switched alignment'
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
        get_undo_manager().begin_transaction()
        fi.set_property('horizontal', self.active)
        get_undo_manager().commit_transaction()

register_action(OrthogonalAlignmentAction, 'ItemFocus', 'Orthogonal')


#
# Association submenu
#

class NavigableAction(CheckAction):
    end_name=''
    def init(self, window):
        self._window = window

    def get_association_end(self):
        return get_parent_focus_item(self._window).get_property(self.end_name)

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            from association import AssociationItem
            if isinstance(item, AssociationItem):
                end = item.get_property(self.end_name)
                if end.subject:
                    self.active = (end.subject.classifier != None)
        except NoFocusItemError:
            pass

    def execute(self):
        item = self.get_association_end()
        assert item.subject
        assert isinstance(item.subject, UML.Property)
        get_undo_manager().begin_transaction()
        item.set_navigable(self.active)
        get_undo_manager().commit_transaction()


class HeadNavigableAction(NavigableAction):
    id = 'Head_isNavigable'
    label = 'Navigable'
    end_name = 'head'

register_action(HeadNavigableAction, 'ItemFocus')


class TailNavigableAction(NavigableAction):
    id = 'Tail_isNavigable'
    label = 'Navigable'
    end_name = 'tail'

register_action(TailNavigableAction, 'ItemFocus')


class AggregationAction(RadioAction):

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
            from association import AssociationItem
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
            get_undo_manager().begin_transaction()
            subject.aggregation = self.aggregation
            get_undo_manager().commit_transaction()


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
            get_undo_manager().begin_transaction()
            item.set_dependency_type(self.dependency_type)
            #item.auto_dependency = False
            self._window.get_action_pool().execute('AutoDependency', active=False)
            get_undo_manager().commit_transaction()
        

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
        get_undo_manager().begin_transaction()
        item.auto_dependency = self.active
        get_undo_manager().commit_transaction()

register_action(AutoDependencyAction, 'ItemFocus')


class IndirectlyInstantiatedComponentAction(CheckAction):
    id = 'IndirectlyInstantiated'
    label = 'Indirectly Instantiated'
    tooltip = 'Indirectly Instantiated Component'

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
        get_undo_manager().begin_transaction()
        item.subject.isIndirectlyInstantiated = self.active
        get_undo_manager().commit_transaction()

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
        get_undo_manager().begin_transaction()
        move(item.subject)
        get_undo_manager().commit_transaction()
        self._window.execute_action('ItemFocus')


class MoveUpAction(MoveAction):
    id = 'MoveUp'
    label = 'Move Up'
    tooltip = 'Move Up'
    move_action = 'moveUp' # name of method to move the element

    def _isSensitive(self, cls, item):
        collection = self._getElements(cls, item)
        return len(collection) > 0 and collection[0] != item.subject

register_action(MoveUpAction, 'ItemFocus')
            

class MoveDownAction(MoveAction):
    id = 'MoveDown'
    label = 'Move Down'
    tooltip = 'Move Down'
    move_action = 'moveDown' # name of method to move the element

    def _isSensitive(self, cls, item):
        collection = self._getElements(cls, item)
        return len(collection) > 0 and collection[-1] != item.subject

register_action(MoveDownAction, 'ItemFocus')


class DummyItem(UML.Element, UML.Presentation):
    pass

class Fold(Action):
    accel = 'C-f'

    def init(self, window):
        self._window = window

    def update(self):
        try:
            item = get_parent_focus_item(self._window)
        except NoFocusItemError:
            pass
        else:
            self.sensitive = self.isSensitive(item)

    def execute(self):
        item = get_parent_focus_item(self._window)
        log.debug('Action %s: %s' % (self.id, item.subject.name))

        get_undo_manager().begin_transaction()

        # TODO: store handle positions, store a special UndoFoldAction.

        # create interface diagram element and assign model element to
        # diagram element
        diag = self._window.get_current_diagram()
        new_item = self.newElement(diag)
        new_item.subject = item.subject

        # center new element diagram in the centre of old one
        x, y = item.get_property('affine')[4:]
        new_item.update_now()
        new_item.move(x + (item.width - new_item.width) / 2.0,
                    y + (item.height - new_item.height) / 2.0)

        # Create a dummy presentation, since we should keep tract of the items subject
        dummy = DummyItem()
        #dummy.canvas = item.canvas
        # Some extra dummy presentations for association ends
        dummy_head_end = DummyItem()
        dummy_tail_end = DummyItem()

        # Find all elements that are connected to our item
        # (Should become (added 10-6-2004 to diacanvas2))
        for connected_handle in item.connected_handles:
        #for connected_item in item.canvas.select(lambda i: i.handles and \
        #                                         (i.handles[0].connected_to is item or \
        #                                          i.handles[-1].connected_to is item)):
            connected_item = connected_handle.owner

            #print 'connected item', connected_item
            # Store the subject, in case of an association also store the
            # head and tail ends subjects
            if connected_item.subject:
                dummy.subject = connected_item.subject
                if isinstance(dummy.subject, UML.Association):
                    dummy_head_end.subject = connected_item.get_property('head_subject')
                    dummy_tail_end.subject = connected_item.get_property('tail_subject')

            # This is the main part. First disconnect, then restore the subject (like if we are
            # loading the model) and at last connect to the new item.
            if connected_item.handles[0].connected_to is item:
                item.disconnect_handle(connected_item.handles[0])
                connected_item.subject = dummy.subject
                new_item.connect_handle(connected_item.handles[0])
            if connected_item.handles[-1].connected_to is item:
                item.disconnect_handle(connected_item.handles[-1])
                connected_item.subject = dummy.subject
                new_item.connect_handle(connected_item.handles[-1])

            assert connected_item.subject is dummy.subject

            # Remove our connected dummy items
            if isinstance(dummy.subject, UML.Association):
                connected_item.set_property('head-subject', dummy_head_end.subject)
                connected_item.set_property('tail-subject', dummy_tail_end.subject)
                del dummy_head_end.subject, dummy_tail_end.subject
            del dummy.subject

        # remove old diagram element
        item.unlink()
        get_undo_manager().commit_transaction()


class UnfoldAction(Fold):
    id = 'Unfold'
    label = '_Unfold'
    tooltip = 'View details'

    def isSensitive(self, item):
        return isinstance(item, InterfaceItem)

    def newElement(self, diag):
        return diag.create(gaphor.diagram.ClassItem)

register_action(UnfoldAction, 'ItemFocus')


class FoldAction(Fold):
    id = 'Fold'
    label = '_Fold'
    tooltip = 'Hide details'

    def isSensitive(self, item):
        return isinstance(item, ClassItem) and isinstance(item.subject, UML.Interface)

    def newElement(self, diag):
        return diag.create(gaphor.diagram.InterfaceItem)

register_action(FoldAction, 'ItemFocus')


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
            self.sensitive = isinstance(item, ClassItem)
            if self.sensitive:
                self.active = self.stereotype in item.subject.appliedStereotype

    def execute(self):
        item = get_parent_focus_item(self._window)
        get_undo_manager().begin_transaction()
        if self.active:
            item.subject.appliedStereotype = self.stereotype
        else:
            del item.subject.appliedStereotype[self.stereotype]
        get_undo_manager().commit_transaction()

