"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easily
attached to a class method and will raise the error dialog when the
method exits with an exception.
"""

import pdb
import sys

from gi.repository import Adw

from gaphor.i18n import gettext


async def error_dialog(message, secondary_message="", window=None):
    _exc_type, _exc_value, exc_traceback = sys.exc_info()
    atty = __debug__ and exc_traceback and sys.stdin.isatty()

    debug_body = (f"{secondary_message}\n\n" if secondary_message else "") + gettext(
        "It looks like Gaphor is started from the command line. Do you want to open a debug session?"
    )
    dialog = Adw.AlertDialog.new(
        message,
        debug_body if atty else secondary_message,
    )
    dialog.add_response("close", gettext("Close"))
    if atty:
        dialog.add_response("debug", gettext("Start Debug Session"))
        dialog.set_default_response("debug")
    else:
        dialog.set_default_response("close")
    dialog.set_close_response("close")

    answer = await dialog.choose(window)

    if exc_traceback and answer in (100, "debug"):
        pdb.post_mortem(exc_traceback)
