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
"""This module has a generic FileDialog class that is used to open
or save files."""

from __future__ import absolute_import
import gtk

class FileDialog(object):
    """This is a file dialog that is used to open or save a file."""
    
    def __init__(self, title, filename=None, action='open', parent=None, multiple=False, filters=[]):
        """Initialize the file dialog.  The title parameter is the title
        displayed in the dialog.  The filename parameter will set the current
        file name in the dialog.  The action is either open or save and changes
        the buttons isplayed.  If the parent window parameter is supplied,
        the file dialog is set to be transient for that window.  The multiple
        parameter should be set to true if sultiple files can be opened at once.
        This means that a list of filenames instead of a single filename string
        will be returned by the selection property.  The filters is a list
        of dictionaries that have a name and pattern key.  This restricts what
        is visible in the dialog."""
        
        self.multiple = multiple
        
        if action == 'open':
            action = gtk.FILE_CHOOSER_ACTION_OPEN
            response_button = gtk.STOCK_OPEN
        else:
            action = gtk.FILE_CHOOSER_ACTION_SAVE
            response_button = gtk.STOCK_SAVE
            
        buttons = (gtk.STOCK_CANCEL,\
                   gtk.RESPONSE_CANCEL,\
                   response_button,\
                   gtk.RESPONSE_OK)
        
        self.dialog = gtk.FileChooserDialog(title=title,
                                            action=action,
                                            buttons=buttons)
                                            
        if parent:
            self.dialog.set_transient_for(parent)
            
        if filename:
            self.dialog.set_current_name(filename)
            
        for filter in filters:
            _filter = gtk.FileFilter()
            _filter.set_name(filter['name'])
            _filter.add_pattern(filter['pattern'])
            self.dialog.add_filter(_filter)
        
    def get_selection(self):
        """Return the selected file or files from the dialog.  This is used
        by the selection property."""
        
        response = self.dialog.run()
        selection = None
        
        if response == gtk.RESPONSE_OK:
            
            if self.multiple:
                selection = self.dialog.get_filenames()
            else:
                selection = self.dialog.get_filename()
            
        return selection
        
    def destroy(self):
        """Destroy the GTK dialog."""
        
        self.dialog.destroy()
                
    selection = property(get_selection)
