# vim:sw=4:et
"""A generic way to handle errors in GUI applications.
"""
import gtk
import sys
import pdb

from gaphor.i18n import _
from gaphor.misc.aspects import Aspect, weave_method

def error_handler(message=None, exc_info=None):
    exc_type, exc_value, exc_traceback = exc_info or sys.exc_info()
    
    if not exc_type:
        return

    if not message:
        message = _('An error occured.')

    buttons = gtk.BUTTONS_OK
    message = '%s\n\nTechnical details:\n\t%s\n\t%s' % (message, exc_type, exc_value)

    if __debug__ and sys.stdin.isatty():
        buttons = gtk.BUTTONS_YES_NO
        message += _('\n\nDo you want to debug?\n(Gaphor should have been started from the command line)')

    dialog = gtk.MessageDialog(None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR,
                    buttons, message)
    answer = dialog.run()
    dialog.destroy()
    if answer == gtk.RESPONSE_YES:
        pdb.post_mortem(exc_traceback)


class ErrorHandlerAspect(Aspect):
    """This aspect raises a Error dialog when the method wrapped by this
    aspect raises an exception. If the application is started from the
    command line, an option is presented to do post-mortem analysis of the
    error.
    """

    def __init__(self, method, message=None):
        self.method = method
        self.message = message

    def after(self, retval, exc):
        if exc:
            error_handler(message=self.message)


if __name__ == '__main__':

    def func(x, y):
        if x == 0:
            raise Exception, 'Raised'
        func(x-1, y)

    try:
        func(5,5)
    except Exception:
        error_handler()

    print 'a'
    print 'a'
    print 'a'
