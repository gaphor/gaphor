"""
Commands related to the Editor
"""
# vim: sw=4:et

import gaphor.UML as UML
from gaphor.misc.action import Action, CheckAction, RadioAction, register_action
import gtk
import diacanvas

from diagramactions import CloseAction

class RunAction(Action):
    id = 'EditorRun'
    label = '_Run'
    tooltip='Execute the code'
    stock_id = 'gtk-execute'

    def init(self, window):
	self._window = window

    def execute(self):
	self._window.run()

register_action(RunAction)


class ClearAction(Action):
    id = 'EditorClear'
    label = '_Clear'
    stock_id = 'gtk-clear'

    def init(self, window):
	self._window = window

    def execute(self):
	self._window.clear_results()

register_action(ClearAction)
