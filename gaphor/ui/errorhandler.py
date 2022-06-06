"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easily
attached to a class' method and will raise the error dialog when the
method exits with an exception.
"""

import pdb
import sys

from gi.repository import Gtk

from gaphor.i18n import gettext


def error_handler(message, secondary_message="", window=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()

    dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR, text=message)
    dialog.set_transient_for(window)

    if __debug__ and exc_traceback and sys.stdin.isatty():
        dialog.props.secondary_text = (
            f"{secondary_message}\n\n" if secondary_message else ""
        ) + gettext(
            "It looks like Gaphor is started from the command line. Do you want to open a debug session?"
        )
        dialog.add_buttons(gettext("Close"), 0, gettext("Start debug session"), 100)
    else:
        dialog.props.secondary_text = secondary_message
        dialog.add_button(gettext("Close"), 0)

    def response(dialog, answer):
        dialog.destroy()
        if exc_traceback and answer == 100:
            pdb.post_mortem(exc_traceback)

    dialog.connect("response", response)
    dialog.set_modal(True)
    dialog.show()
