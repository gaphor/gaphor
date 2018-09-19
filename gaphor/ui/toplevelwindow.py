#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
"""
Basic stuff for toplevel windows.
"""

from __future__ import absolute_import
import os.path
import pkg_resources
import gtk
from zope import interface
from .interfaces import IUIComponent


ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)

class ToplevelWindow(object):

    interface.implements(IUIComponent)

    menubar_path = ''
    toolbar_path = ''
    resizable = True

    def __init__(self):
        self.window = None

    def ui_component(self):
        raise NotImplementedError

    def construct(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (gtk.gdk.pixbuf_new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        
        if self.menubar_path or self.toolbar_path:
            # Create a full featured window.
            vbox = gtk.VBox()
            self.window.add(vbox)
            vbox.show()

            menubar = self.ui_manager.get_widget(self.menubar_path)
            if menubar:
                vbox.pack_start(menubar, expand=False)
            
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(toolbar, expand=False)

            vbox.pack_end(self.ui_component(), expand=self.resizable)
            vbox.show()
            # TODO: add statusbar
        else:
            # Create a simple window.
            self.window.add(self.ui_component())
        self.window.show()


# vim:sw=4:et:ai
