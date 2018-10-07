# vim:sw=4:et
"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easely attached
to a class' method and will raise the error dialog when the method exits with
an exception.
"""
from gi.repository import Gtk
import sys
import pdb

from gaphor.i18n import _

def error_handler(message=None, exc_info=None):
    exc_type, exc_value, exc_traceback = exc_info or sys.exc_info()
    
    if not exc_type:
        return

    if not message:
        message = _('An error occured.')

    buttons = Gtk.ButtonsType.OK
    message = '%s\n\nTechnical details:\n\t%s\n\t%s' % (message, exc_type, exc_value)

    if __debug__ and sys.stdin.isatty():
        buttons = Gtk.ButtonsType.YES_NO
        message += _('\n\nDo you want to debug?\n(Gaphor should have been started from the command line)')

    dialog = Gtk.MessageDialog(None,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    buttons, message)
    answer = dialog.run()
    dialog.destroy()
    if answer == Gtk.ResponseType.YES:
        pdb.post_mortem(exc_traceback)

# vim:sw=4:et:ai
