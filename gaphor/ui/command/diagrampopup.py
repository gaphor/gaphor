"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command, StatefulCommand
from commandinfo import CommandInfo
import gaphor.UML as UML
import diacanvas
import gaphor.diagram as diagram

CONTEXT='diagram.popup'

class NoFocusItemError(GaphorError):
    pass

def get_parent_focus_item(window):
    """Get the outer most focus item (the obe that's not a composite)."""
    fi = window.get_view().focus_item
    if fi:
	item = fi.item
	while (item.flags & diacanvas.COMPOSITE) != 0:
	    item = item.parent
	return item
    raise NoFocusItemError, 'No item has focus.'

# NOTE: attributes and operations can now only be created on classes,
#       actors and uuse-cases are also classifiers, but we can't add 
#       attrs and opers via the UI right now.

#class CreateAttributeCommand(Command):
#
#    def set_parameters(self, params):
#	self._window = params['window']
#
#    def execute(self):
#	subject = get_parent_focus_item(self._window).subject
#	assert isinstance(subject, UML.Classifier)
#	elemfact = GaphorResource(UML.ElementFactory)
#	attribute = elemfact.create(UML.Attribute)
#	attribute.name = 'new'
#	subject.feature = attribute

#CommandInfo (name='CreateAttribute', _label='New _Attribute',
#	     _tip='Create a new attribute',
#	     context=CONTEXT, subject=UML.Class,
#	     sensitive=('show-attributes',),
#	     command_class=CreateAttributeCommand).register()

class CreateOperationCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	subject = get_parent_focus_item(self._window).subject
	assert isinstance(subject, UML.Classifier)
	elemfact = GaphorResource(UML.ElementFactory)
	operation = elemfact.create(UML.Operation)
	operation.name = 'new'
	subject.feature = operation

CommandInfo (name='CreateOperation', _label='New _Operation',
	     _tip='Create a new operation',
	     context=CONTEXT, subject=UML.Class,
	     sensitive=('show-operations',),
	     command_class=CreateOperationCommand).register()


class DeleteFeatureCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	#subject = get_parent_focus_item(self._window).subject
	subject = self._window.get_view().focus_item.item.subject
	assert isinstance(subject, UML.Feature)
	subject.undoable_unlink()

#CommandInfo (name='DeleteAttribute', _label='Delete A_ttribute',
#	     _tip='Delete the selected attribute',
#	     context=CONTEXT, subject=UML.Attribute,
#	     sensitive=('show-attributes',),
#	     command_class=DeleteFeatureCommand).register()

CommandInfo (name='DeleteOperation', _label='Delete O_peration',
	     _tip='Delete the selected operation',
	     context=CONTEXT, subject=UML.Operation,
	     sensitive=('show-operations',),
	     command_class=DeleteFeatureCommand).register()


class ShowAttributesCommand(StatefulCommand):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self, new_state):
	item = get_parent_focus_item(self._window)
	item.set_property('show-attributes', new_state)

CommandInfo (name='ShowAttributes', _label='Show Attributes',
	     _tip='show attribute compartment',
	     context=CONTEXT, subject=diagram.ClassItem,
	     state=('show-attributes',),
	     command_class=ShowAttributesCommand).register()


class ShowOperationsCommand(StatefulCommand):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self, new_state):
	item = get_parent_focus_item(self._window)
	item.set_property('show-operations', new_state)

CommandInfo (name='ShowOperations', _label='Show Operations',
	     _tip='show attribute compartment',
	     context=CONTEXT, subject=diagram.ClassItem,
	     state=('show-operations',),
	     command_class=ShowOperationsCommand).register()

#
# Lines:
#

class SegmentCommand(Command):
    """Base class for add and delete line segment."""

    def set_parameters(self, params):
	self._window = params['window']
	self._coords = params['coords']

    def get_item_and_segment(self):
	fi = get_parent_focus_item(self._window)
	view = self._window.get_view()
	assert isinstance(fi, diacanvas.CanvasLine)
	wx, wy = view.window_to_world(self._coords[0], self._coords[1])
	x, y = fi.affine_point_w2i(wx, wy)
	segment = fi.get_closest_segment(x, y)
	return (fi, segment)

class AddSegmentCommand(SegmentCommand):

    def execute(self):
	item, segment = self.get_item_and_segment()
	if item:
	    item.set_property('add_segment', segment)
	    
CommandInfo (name='AddSegment', _label='Add _Segment',
	     _tip='Add a segment to the line',
	     context=CONTEXT, subject=diacanvas.CanvasLine,
	     command_class=AddSegmentCommand).register()

class DeleteSegmentCommand(SegmentCommand):

    def execute(self):
	item, segment = self.get_item_and_segment()
	if item:
	    item.set_property('del_segment', segment)
	    
CommandInfo (name='DeleteSegment', _label='Delete _Segment',
	     _tip='Delete the segment from the line',
	     sensitive=('del_segment',),
	     context=CONTEXT, subject=diacanvas.CanvasLine,
	     command_class=DeleteSegmentCommand).register()

class OrthogonalCommand(StatefulCommand):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self, orthogonal):
	fi = get_parent_focus_item(self._window)
	view = self._window.get_view()
	assert isinstance(fi, diacanvas.CanvasLine)
	#orthogonal = not fi.get_property('orthogonal')
	log.debug('Setting orthogonal for %s: %d' % (fi, orthogonal))
	if orthogonal and len(fi.handles) < 3:
	    fi.set_property('add_segment', 0)
	fi.set_property('orthogonal', orthogonal)
	#import traceback
	#traceback.print_stack()

CommandInfo (name='Orthogonal', _label='Orthogonal',
	     _tip='Set the line to orthogonal',
	     subject=diacanvas.CanvasLine,
	     context=CONTEXT, state=('orthogonal',),
	     command_class=OrthogonalCommand).register()

#
# Association submenu
#

class NavigableCommand(StatefulCommand):

    def set_parameters(self, params):
	self._window = params['window']

    def get_association_end(self):
	raise NotImplementedError

    def execute(self, new_state):
	subject = self.get_association_end()
	assert isinstance(subject, UML.AssociationEnd)
	subject.isNavigable = new_state #not subject.isNavigable


class HeadNavigableCommand(NavigableCommand):

    def get_association_end(self):
	return get_parent_focus_item(self._window).head_end

CommandInfo (name='Head_isNavigable', _label='Navigable',
	     _tip='',
	     subject=UML.Association,
	     context=CONTEXT, state=('head_is_navigable',),
	     command_class=HeadNavigableCommand).register()


class TailNavigableCommand(NavigableCommand):

    def get_association_end(self):
	return get_parent_focus_item(self._window).tail_end

CommandInfo (name='Tail_isNavigable', _label='Navigable',
	     _tip='',
	     subject=UML.Association,
	     context=CONTEXT, state=('tail_is_navigable',),
	     command_class=TailNavigableCommand).register()


class AggregationCommand(StatefulCommand):

    def set_parameters(self, params):
	self._window = params['window']

    def get_association_end(self):
	raise NotImplementedError

    def execute(self, new_state):
	if new_state:
	    subject = self.get_association_end()
	    assert isinstance(subject, UML.AssociationEnd)
	    subject.aggregation = self.aggregation


class HeadAggregationCommand(AggregationCommand):

    def get_association_end(self):
	return get_parent_focus_item(self._window).head_end


class TailAggregationCommand(AggregationCommand):

    def get_association_end(self):
	return get_parent_focus_item(self._window).tail_end


class HeadNoneCommand(HeadAggregationCommand):
    aggregation = 'none'

CommandInfo (name='Head_None', _label='None',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('head_ak_none',),
	     command_class=HeadNoneCommand).register()


class HeadAggregateCommand(HeadAggregationCommand):
    aggregation = 'aggregate'

CommandInfo (name='Head_Aggregate', _label='Aggregate',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('head_ak_aggregate',),
	     command_class=HeadAggregateCommand).register()


class HeadCompositeCommand(HeadAggregationCommand):
    aggregation = 'COMPOSITE'

CommandInfo (name='Head_Composite', _label='Composite',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('head_ak_composite',),
	     command_class=HeadCompositeCommand).register()


class TailNoneCommand(TailAggregationCommand):
    aggregation = 'NONE'

CommandInfo (name='Tail_None', _label='None',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('tail_ak_none',),
	     command_class=TailNoneCommand).register()


class TailAggregateCommand(TailAggregationCommand):
    aggregation = 'UML.AK_AGGREGATE'

CommandInfo (name='Tail_Aggregate', _label='Aggregate',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('tail_ak_aggregate',),
	     command_class=TailAggregateCommand).register()


class TailCompositeCommand(TailAggregationCommand):
    aggregation = 'UML.AK_COMPOSITE'

CommandInfo (name='Tail_Composite', _label='Composite',
	     _tip='', subject=UML.Association,
	     context=CONTEXT, state=('tail_ak_composite',),
	     command_class=TailCompositeCommand).register()

