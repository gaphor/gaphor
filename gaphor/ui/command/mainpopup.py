"""
Commands related to the TreeModel/View
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.UML as UML

class OpenCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']
	self._element = params['element']

    def execute(self):
	if isinstance(self._element, UML.Diagram):
	    # Import here to avoid cyclic references
	    from gaphor.ui import DiagramWindow
	    newwin = DiagramWindow()
	    newwin.construct()
	    self._window.add_transient_window(newwin)
	    newwin.set_diagram(self._element)
	else:
	    log.debug('No action defined for element %s' % self._element.__class__.__name__)

CommandInfo (name='OpenModelElement', _label='_Open',
	     context='main.popup',
	     popup=UML.Diagram,
	     command_class=OpenCommand).register()


class RenameCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']
	self._element = params['element']
	self._path = params['path']

    def execute(self):
	view = self._window.get_view()
	column = view.get_column(0)
	cell = column.get_cell_renderers()[1]
	cell.set_property('editable', 1)
	cell.set_property('text', self._element.name)
	view.set_cursor(self._path, column, True)
	cell.set_property('editable', 0)

CommandInfo (name='RenameModelElement', _label='_Rename',
	     context='main.popup',
	     command_class=RenameCommand).register()


