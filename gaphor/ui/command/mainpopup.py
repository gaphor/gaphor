"""
Commands related to the TreeModel/View
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo

class OpenModelElementCommand(Command):

    def set_parameters(self, params):
	self.__window = params['window']
	self.__element = params['element']

    def execute(self):
	from gaphor.UML import Diagram
	if isinstance(self.__element, Diagram):
	    # Import here to avoid cyclic references
	    from gaphor.ui import DiagramWindow
	    log.debug('Opening Diagram: %s' % self.__element.name)
	    #winfact = GaphorResource (WindowFactory)
	    #winfact.create (DiagramWindow, diagram=self.__element)
	    newwin = DiagramWindow()
	    newwin.construct()
	    # Also listen to the key accelerators of the owner window
	    self.__window.add_transient_window(newwin)
	    newwin.set_diagram(self.__element)
	    #def handle_wr(x):
		#print 'diag_win died:', x
	    #import weakref
	    #self.wr = weakref.ref (diag_win, handle_wr)
	else:
	    log.debug('No action defined for element %s' % self.__element.__class__.__name__)

CommandInfo (name='OpenModelElement', _label='_Open',
	     context='main.popup',
	     command_class=OpenModelElementCommand).register()

