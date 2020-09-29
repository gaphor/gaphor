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

    if 0 and __debug__ and exc_traceback and sys.stdin.isatty():
        buttons = Gtk.ButtonsType.YES_NO
        secondary_message += ("\n\n" if secondary_message else "") + gettext(
            "It looks like Gaphor is started from the command line.\nDo you want to open a debug session?"
        )
    else:
        buttons = Gtk.ButtonsType.OK

    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        Gtk.MessageType.ERROR,
        buttons,
    )
    dialog.props.text = message
    dialog.props.secondary_text = secondary_message
    dialog.set_transient_for(window)
    answer = dialog.run()
    dialog.destroy()

    if exc_traceback and answer == Gtk.ResponseType.YES:
        pdb.post_mortem(exc_traceback)
