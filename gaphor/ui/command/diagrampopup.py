"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.UML as UML
import diacanvas

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
	     sensitive=('focus',), popup=UML.Classifier,
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
	     sensitive=('focus',), popup=UML.Classifier,
	     command_class=CreateOperationCommand).register()

