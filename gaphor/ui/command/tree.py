"""
Commands related to the TreeModel/View
"""
# vim: sw=4

from gaphor.misc.command import Command
import gaphor.UML as UML

class OpenModelElementCommand(Command):

    def __init__(self, element):
	Command.__init__(self)
	self.element = element

    def execute(self):
	if isinstance(self.element, UML.Diagram):
	    print 'Opening Diagram', self.element.name
	else:
	    print 'No action defined for element', self.element.__class__.__name__
