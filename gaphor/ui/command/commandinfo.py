# vim:sw=4
"""
This module contains the class CommandInfo, which is used to store meta data
about commands. The gaphor.ui modules make use of this class to set
the state of GUI components (esp. menu items).
"""
from operator import isSequenceType
import gaphor.UML as UML
from gaphor.misc.command import Command

class CommandInfo(object):
    """CommandInfo contains meta information about a command. The following
    """
    __slots__ = ( 'name', '_label', 'context', '_tip',
		  'sensitive', 'state', 'subject', 'pixtype', 'pixname',
		  'accel', 'command_class', 'extra_args' )

    def __init__(self, name, _label, context, _tip=None,
		 sensitive=None, state=None, subject=None,
		 pixtype='stock', pixname=None, accel=None,
		 command_class=None):
	"""Create a new command info object."""
	assert name and name != ''
	assert not subject or issubclass(subject, UML.ModelElement)
	assert issubclass(command_class, Command)

	self.name = name
	self._label = _label
	self.context = context
	self._tip = _tip
	if sensitive and not isSequenceType(sensitive):
	    self.sensitive = (sensitive,)
	else:
	    self.sensitive = sensitive
	if state and not isSequenceType(state):
	    self.state = (state,)
	else:
	    self.state = state
	self.subject = subject
	self.pixtype = pixtype
	self.pixname = pixname
	self.accel = accel
	self.command_class = command_class

    def create_cmd_xml(self):
	xml = '<cmd name="%s" _label="%s"' % (self.name, self._label)
	if self._tip:
	    xml += ' _tip="%s"' % self._tip
	#if self.sensitive:
	#    xml += ' sensitive="1"'
	# Set the state property, so the framework knows it can expect
	# state changes
	#if self.state:
	#    xml += ' type="toggle"'
	if self.pixname:
	    xml += ' pixtype="%s" pixname="%s"' % (self.pixtype, self.pixname)
        if self.accel:
	    xml += ' accel="%s"' % self.accel
	xml += '/>'
	return xml

    def register(self):
	"""Add the CommandInfo to a CommandRegistry, this should make it
	easely accessible."""
	GaphorResource('CommandRegistry').register(self)

