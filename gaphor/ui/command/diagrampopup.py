"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.UML as UML
import diacanvas

# NOTE: attributes and operations can now only be created on classes,
#       actors and uuse-cases are also classifiers, but we can't add 
#       attrs and opers via the UI right now.

class CreateAttributeCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	fi = self._window.get_view().focus_item
	if fi:
	    fi = fi.item
	    while (fi.flags & diacanvas.COMPOSITE) != 0:
		fi = fi.parent
	    subject = fi.subject
	    assert isinstance(subject, UML.Classifier)
	    elemfact = GaphorResource(UML.ElementFactory)
	    attribute = elemfact.create(UML.Attribute)
	    attribute.name = 'new'
	    subject.feature.append(attribute)
	    
CommandInfo (name='CreateAttribute', _label='New _Attribute',
	     _tip='Create a new attribute',
	     context='diagram.popup',
	     sensitive=('focus',), subject=UML.Class,
	     command_class=CreateAttributeCommand).register()

class CreateOperationCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	fi = self._window.get_view().focus_item
	if fi:
	    fi = fi.item
	    while (fi.flags & diacanvas.COMPOSITE) != 0:
		fi = fi.parent
	    subject = fi.subject
	    assert isinstance(subject, UML.Classifier)
	    elemfact = GaphorResource(UML.ElementFactory)
	    operation = elemfact.create(UML.Operation)
	    operation.name = 'new'
	    subject.feature.append(operation)
	    
CommandInfo (name='CreateOperation', _label='New _Operation',
	     _tip='Create a new operation',
	     context='diagram.popup',
	     sensitive=('focus',), subject=UML.Class,
	     command_class=CreateOperationCommand).register()


class SegmentCommand(Command):
    """Base class for add and delete line segment."""

    def set_parameters(self, params):
	self._window = params['window']
	self._coords = params['coords']

    def get_item_and_segment(self):
	view = self._window.get_view()
	fi = view.focus_item
	if fi:
	    fi = fi.item
	    while (fi.flags & diacanvas.COMPOSITE) != 0:
		fi = fi.parent
	    assert isinstance(fi, diacanvas.CanvasLine)
	    wx, wy = view.window_to_world(self._coords[0], self._coords[1])
	    x, y = fi.affine_point_w2i(wx, wy)
	    segment = fi.get_closest_segment(x, y)
	    return (fi, segment)
	return (None, 0)

class AddSegmentCommand(SegmentCommand):

    def execute(self):
	item, segment = self.get_item_and_segment()
	if item:
	    item.set_property('add_segment', segment)
	    
CommandInfo (name='AddSegment', _label='Add _Segment',
	     _tip='Add a segment to the line',
	     context='diagram.popup',
	     sensitive=('focus',), subject=diacanvas.CanvasLine,
	     command_class=AddSegmentCommand).register()

class DeleteSegmentCommand(SegmentCommand):

    def execute(self):
	item, segment = self.get_item_and_segment()
	if item:
	    item.set_property('del_segment', segment)
	    
CommandInfo (name='DeleteSegment', _label='Delete _Segment',
	     _tip='Delete the segment from the line',
	     context='diagram.popup',
	     sensitive=('focus',), subject=diacanvas.CanvasLine,
	     command_class=DeleteSegmentCommand).register()

