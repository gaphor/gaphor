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

    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        Gtk.MessageType.ERROR,
    )
    dialog.props.text = message

    if __debug__ and exc_traceback and sys.stdin.isatty():
        dialog.props.secondary_text = ("\n\n" if secondary_message else "") + gettext(
            "It looks like Gaphor is started from the command line. Do you want to open a debug session?"
        )
        dialog.add_buttons(Gtk.STOCK_CLOSE, 0, gettext("Start debug session"), 100)
    else:
        dialog.props.secondary_text = secondary_message
        dialog.add_button(Gtk.STOCK_OK, 0)

    dialog.set_transient_for(window)
    answer = dialog.run()
    dialog.destroy()

    if exc_traceback and answer == 100:
        pdb.post_mortem(exc_traceback)
