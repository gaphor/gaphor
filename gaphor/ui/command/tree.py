"""
Commands related to the TreeModel/View
"""
# vim: sw=4

from gaphor.misc.command import Command
import gaphor.UML as UML

class OpenModelElementCommand(Command):

    def __init__(self, element):
	Command.__init__(self)
	self.__element = element

    def execute(self):
	if isinstance(self.__element, UML.Diagram):
	    # Import here to avoid cyclic references
	    from gaphor.ui import DiagramWindow
	    print 'Opening Diagram', self.__element.name
	    DiagramWindow(self.__element)
	else:
	    print 'No action defined for element', self.__element.__class__.__name__
