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
	    print 'Opening Diagram', self.__element.name
	    #winfact = GaphorResource (WindowFactory)
	    #winfact.create (DiagramWindow, diagram=self.__element)
	    newwin = DiagramWindow()
	    newwin.construct()
	    # Also listen to the key accelerators of the owner window
	    main_win = self.__window.get_window()
	    diag_win = newwin.get_window()
	    diag_win.add_accel_group(main_win.get_accel_group())
	    diag_win.set_transient_for (main_win)
	    newwin.set_diagram(self.__element)
	    def handle_wr(x):
		print 'diag_win died:', x
	    import weakref
	    self.wr = weakref.ref (diag_win, handle_wr)
	else:
	    print 'No action defined for element', self.__element.__class__.__name__

CommandInfo (name='OpenModelElement', _label='_Open',
	     context='main.popup',
	     command_class=OpenModelElementCommand).register()

