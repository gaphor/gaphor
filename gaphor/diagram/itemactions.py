"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action

from klass import ClassItem
from nameditem import NamedItem
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

class ItemRenameAction(Action):
    id = 'ItemRename'
    label = '_Rename'
    tooltip = 'Rename selected item'

    def init(self, window):
        self._window = window

    def update(self):
	try:
	    item = get_parent_focus_item(self._window)
	except NoFocusItemError:
	    self.sensitive = False
	else:
	    if isinstance(item, NamedItem):
		self.sensitive = True

    def execute(self):
        item = self._window.get_current_diagram_view().focus_item.item
	item.edit()

register_action(ItemRenameAction, 'ItemFocus')


class EditItemAction(Action):
    id = 'EditItem'
    label = 'Edit'
    tooltip='Edit'

    def init(self, window):
        self._window = window

    def execute(self):
        item = self._window.get_current_diagram_view().focus_item.item
        #assert isinstance(subject, (UML.Property, UML.Operation))
        item.edit()

register_action(EditItemAction, 'ItemFocus')


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
        item.subject.isAbstract = self.active

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
        subject = get_parent_focus_item(self._window).subject
        assert isinstance(subject, UML.Class)
        elemfact = gaphor.resource(UML.ElementFactory)
        attribute = elemfact.create(UML.Property)
        attribute.name = 'new'
        subject.ownedAttribute = attribute
	# TODO: Select this item for editing

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
        subject = get_parent_focus_item(self._window).subject
        assert isinstance(subject, UML.Classifier)
        elemfact = gaphor.resource(UML.ElementFactory)
        operation = elemfact.create(UML.Operation)
        operation.name = 'new'
        subject.ownedOperation = operation
	# TODO: Select this item for editing

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
        item.set_property('show-attributes', self.active)

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
        item.set_property('show-operations', self.active)

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
            item.set_property('add_segment', segment)
            
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
        view = self._window.get_current_diagram_view()
        assert isinstance(fi, diacanvas.CanvasLine)
        #orthogonal = not fi.get_property('orthogonal')
        #log.debug('Setting orthogonal for %s: %d' % (fi, orthogonal))
        if self.active and len(fi.handles) < 3:
            fi.set_property('add_segment', 0)
        fi.set_property('orthogonal', self.active)
        #import traceback
        #traceback.print_stack()

register_action(OrthogonalAction, 'ItemFocus', 'AddSegment', 'DeleteSegment')


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
		    self.active = (end.subject.class_ != None)
        except NoFocusItemError:
	    pass

    def execute(self):
        item = self.get_association_end()
        assert item.subject
	assert isinstance(item.subject, UML.Property)
	item.set_navigable(self.active)


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
            subject.aggregation = self.aggregation


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
