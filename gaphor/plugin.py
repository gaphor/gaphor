# vim:sw=4:et
"""This module provides everything needed to create a plugin.

Application - Get/set application wide resources
import_plugin - The save way to import other plugins into your plugin.

Classes to construct Actions:
    Action
    CheckAction (Checkbutton Action)
    RadioAction (RadioButton Action, should set the group attribute)
    ObjectAction (this is not an action, but it contains some code to make
                  instances of Actions behave like Action classes)

Each action is initialized. The window containing the action can be accessed
by the 'window' property.
"""

import sys
import os.path
from gaphor.application import Application

from gaphor.misc.action import Action as _Action
from gaphor.misc.action import CheckAction as _CheckAction
from gaphor.misc.action import RadioAction as _RadioAction
from gaphor.misc.action import ObjectAction
from gaphor.i18n import _

import gtk

def import_plugin(name):
    """
    A normal 'import gaphor._plugins.<name>' doesn't work.
    Use this function instead.
    """
    from gaphor.pluginmanager import MODULENS
    mod = sys.modules[MODULENS + name]
    return mod

class _ActionMixIn(object):
    """
    Handle initialization of actions in a way that the main window
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

class DiagramExportAction(Action):
    """
    Diagram export action allows to save a diagram into filename.
    Deriving classes should:: 
        - implement save method
        - define title attribute
        - define file extension
    """
    title = None # gtk file chooser title
    ext   = None # file extension, like .svg

    def update(self):
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False


    def execute(self):
        filename = (self.get_window().get_current_diagram().name or 'export') + self.ext
        filesel = gtk.FileChooserDialog(title = self.title,
            action = gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        filesel.set_current_name(filename)

        save = False
        while True:
            response = filesel.run()
            filename = filesel.get_filename()

            if response == gtk.RESPONSE_OK:
                if os.path.exists(filename):
                    dialog = gtk.MessageDialog(filesel,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                        _("The file %s already exists. Do you want to replace it with the file you are exporting to?") % filename)
                    answer = dialog.run()
                    dialog.destroy()
                    if answer == gtk.RESPONSE_YES:
                        save = True
                        break
                else:
                    save = True
                    break
            else:
                break

        if save and filename:
            self.save(filename)
        filesel.destroy()


    def save(self, filename):
        raise NotImplementedError, 'save method should be implemented'


del _Action, _CheckAction, _RadioAction, _ActionMixIn

