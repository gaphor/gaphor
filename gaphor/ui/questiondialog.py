
"""Defines a QuestionDialog class used to get a yes or no answer from the user.
"""

import gtk

class QuestionDialog(object):
    """A dialog that displays a GTK MessageDialog to get a yes or no answer
    from the user."""
    
    def __init__(self, question, parent=None):
        """Create the QuestionDialog.  The question parameter is a question
        string to ask the user.  The parent parameter is the parent window
        of the dialog."""
        
        self.dialog = gtk.MessageDialog(parent,\
                                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,\
                                        gtk.MESSAGE_QUESTION,\
                                        gtk.BUTTONS_YES_NO,\
                                        question)
                                        
    def get_answer(self):
        """Return answer to the question by running the dialog.  The answer
        is accessed via the answer attribute."""
        
        answer = self.dialog.run()
        
        if answer == gtk.RESPONSE_YES:
            return True
            
        return False
        
    def destroy(self):
        """Destroy the GTK dialog."""
        
        self.dialog.destroy()

    answer = property(get_answer)
