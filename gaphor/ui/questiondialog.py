#!/usr/bin/env python

# Copyright (C) 2010-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""Defines a QuestionDialog class used to get a yes or no answer from the user.
"""

from __future__ import absolute_import
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
