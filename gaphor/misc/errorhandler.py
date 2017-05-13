#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""A generic way to handle errors in GUI applications.

This module also contains a ErrorHandlerAspect, which can be easely attached
to a class' method and will raise the error dialog when the method exits with
an exception.
"""
from __future__ import absolute_import
import gtk
import sys
import pdb

from gaphor.i18n import _

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

# vim:sw=4:et:ai
