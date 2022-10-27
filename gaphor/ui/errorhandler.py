"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easily
attached to a class method and will raise the error dialog when the
method exits with an exception.
"""

import pdb
import sys

from gi.repository import Gtk

if Gtk.get_major_version() == 4:
    from gi.repository import Adw

from gaphor.i18n import gettext


def error_handler(message, secondary_message="", window=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()

    body = (f"{secondary_message}\n\n" if secondary_message else "") + gettext(
        "It looks like Gaphor is started from the command line. Do you want to open a debug session?"
    )
    if Gtk.get_major_version() == 3:
        dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR, text=message)
        dialog.set_transient_for(window)

        if __debug__ and exc_traceback and sys.stdin.isatty():
            dialog.props.secondary_text = body
            dialog.add_buttons(gettext("Close"), 0, gettext("Start Debug Session"), 100)
        else:
            dialog.props.secondary_text = secondary_message
            dialog.add_button(gettext("Close"), 0)
        dialog.set_modal(True)
    else:
        dialog = Adw.MessageDialog.new(
            window,
            message,
        )
        dialog.set_body(body)
        if __debug__ and exc_traceback and sys.stdin.isatty():
            dialog.add_response("close", gettext("Close"))
            dialog.add_response("debug", gettext("Start Debug Session"))
            dialog.set_default_response("debug")
        else:
            dialog.add_response("close", gettext("Close"))
            dialog.set_default_response("close")
        dialog.set_close_response("close")

    def response(dialog, answer):
        dialog.destroy()
        if exc_traceback and answer in [100, "debug"]:
            pdb.post_mortem(exc_traceback)

    dialog.connect("response", response)
    dialog.show()
