"""
Commands related to the Editor
"""
# vim: sw=4

from gaphor.misc.command import Command
from commandinfo import CommandInfo
import gaphor.UML as UML
import gtk
import diacanvas

class CloseCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	self._window.close()

CommandInfo (name='FileClose', _label='_Close', pixname='Close',
	     _tip='Close the diagram window',
	     accel='*Control*w',
	     context='editor.menu',
	     command_class=CloseCommand).register()


class RunCommand(Command):

    def set_parameters(self, params):
	self._window = params['window']

    def execute(self):
	self._window.run()

CommandInfo (name='EditorRun', _label='_Run', pixname='gtk-execute',
	     _tip='Execute the code',
	     context='editor.menu',
	     command_class=RunCommand).register()

