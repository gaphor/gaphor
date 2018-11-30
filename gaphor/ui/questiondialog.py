"""Defines a QuestionDialog class used to get a yes or no answer from the user.
"""

from builtins import object
from gi.repository import Gtk


class QuestionDialog(object):
    """A dialog that displays a GTK MessageDialog to get a yes or no answer
    from the user."""

    def __init__(self, question, parent=None):
        """Create the QuestionDialog.  The question parameter is a question
        string to ask the user.  The parent parameter is the parent window
        of the dialog."""

        self.dialog = Gtk.MessageDialog(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            question,
        )

    def get_answer(self):
        """Return answer to the question by running the dialog.  The answer
        is accessed via the answer attribute."""

        answer = self.dialog.run()

        if answer == Gtk.ResponseType.YES:
            return True

        return False

    def destroy(self):
        """Destroy the GTK dialog."""

        self.dialog.destroy()

    answer = property(get_answer)
