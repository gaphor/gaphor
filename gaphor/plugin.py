# vim:sw=4:et
"""This module provides everything needed to create a plugin.

resource - Get/set application wide resources

Classes to construct Actions:
    Action
    CheckAction (Checkbutton Action)
    RadioAction (RadioButton Action, should set the group attribute)
    ObjectAction (this is not an action, but it contains some code to make
                  instances of Actions behave like Action classes)

Each action is initialized. The window containing the action can be accessed
by the 'window' property.
"""

from gaphor import resource

from gaphor.misc.action import Action as _Action
from gaphor.misc.action import CheckAction as _CheckAction
from gaphor.misc.action import RadioAction as _RadioAction
from gaphor.misc.action import ObjectAction


class _ActionMixIn(object):
    """Handle initialization of actions in a way that the main window
    can properly initialize the action.
    """

    def init(self, window):
        self._window = window

    def get_window(self):
        return self._window

    window = property(get_window)

class Action(_Action, _ActionMixIn): pass
class CheckAction(_CheckAction, _ActionMixIn): pass
class RadioAction(_RadioAction, _ActionMixIn): pass

del _Action, _CheckAction, _RadioAction, _ActionMixIn

