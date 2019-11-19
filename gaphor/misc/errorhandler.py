"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easily attached
to a class' method and will raise the error dialog when the method exits with
an exception.
"""

import pdb
import sys

from gi.repository import Gtk

from gaphor.i18n import gettext


def error_handler(message=None, exc_info=None):
    exc_type, exc_value, exc_traceback = exc_info or sys.exc_info()

    if not exc_type:
        return

    if not message:
        message = gettext("An error occurred.")

    buttons = Gtk.ButtonsType.OK
    message = (
        f"{message}\n\n"
        + gettext("Technical details:")
        + f"\n\t{exc_type}\n\t{exc_value}"
    )

    if __debug__ and sys.stdin.isatty():
        buttons = Gtk.ButtonsType.YES_NO
        message += "\n\n" + gettext(
            "Do you want to debug?\n(Gaphor should have been started from the command line)"
        )

    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        Gtk.MessageType.ERROR,
        buttons,
        message,
    )
    answer = dialog.run()
    dialog.destroy()
    if answer == Gtk.ResponseType.YES:
        pdb.post_mortem(exc_traceback)
