"""
Commands related to the TreeModel/View
"""
# vim: sw=4

from gaphor.misc.command import Command
import gaphor.UML as UML

class OpenModelElementCommand(Command):

    def __init__(self, element, **args):
	Command.__init__(self, **args)
	self.__element = element

    def execute(self):
	if isinstance(self.__element, UML.Diagram):
	    # Import here to avoid cyclic references
	    from gaphor.ui import DiagramWindow, WindowFactory
	    print 'Opening Diagram', self.__element.name
	    winfact = GaphorResource (WindowFactory)
	    winfact.create (DiagramWindow, diagram=self.__element)
	else:
	    print 'No action defined for element', self.__element.__class__.__name__
