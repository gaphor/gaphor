#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
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
"""About and help services. (help browser anyone?)"""

from __future__ import absolute_import
from logging import getLogger
import os
import pkg_resources
import gtk
from zope import interface

from gaphor.application import Application
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, build_action_group

class HelpService(object):

    interface.implements(IService, IActionProvider)

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="help">
            <placeholder name="ternary">
              <menuitem action="help-about" />
            </placeholder>
          </menu>
        </menubar>
      </ui>
    """

    main_window = inject('main_window')
    logger = getLogger('HelpService')

    def __init__(self):
        pass

    def init(self, app):
        self.logger.info('Starting')
        self.action_group = build_action_group(self)

    def shutdown(self):
        self.logger.info('Shutting down')

    @action(name='help-about', stock_id='gtk-about')
    def about(self):
        logo_file =  os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'ui', 'pixmaps', 'logo.png')
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        version = Application.distribution.version
        about = gtk.Dialog(_('About Gaphor'), self.main_window.window, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
        about.set_default_response(gtk.RESPONSE_OK)
        vbox = about.vbox

        image = gtk.Image()
        image.set_from_pixbuf(logo)
        vbox.pack_start(image)

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(4)
        notebook.set_tab_pos(gtk.POS_BOTTOM)
        vbox.pack_start(notebook)

        tab_vbox = gtk.VBox()

        def add_label(text, padding_x=0, padding_y=0):
            label = gtk.Label(text)
            label.set_property('use-markup', True)
            label.set_padding(padding_x, padding_y)
            label.set_justify(gtk.JUSTIFY_CENTER)
            tab_vbox.pack_start(label)

        add_label('<span weight="bold">version %s</span>' % version)
        add_label('<span variant="smallcaps">The UML and SysML(soon!) Modeling Tool</span>', 8, 8)
        add_label('<span size="small">Copyright (c) 2001-2007 Arjan J. Molenaar, 2017 Dan Yeaw</span>', 8, 8)

        notebook.append_page(tab_vbox, gtk.Label(_('About')))

        tab_vbox = gtk.VBox()
        
        add_label('This software is published\n'
                  'under the terms of the\n'
                  '<span weight="bold">GNU General Public License v2</span>.\n'
                  'See the LICENSE.txt file for details.', 0, 8)
        notebook.append_page(tab_vbox, gtk.Label(_('License')))

        tab_vbox = gtk.VBox()
        
        add_label('Gaphor is written by:\n'
                  'Dan Yeaw\n'
                  'Arjan Molenaar\n'
                  'Artur Wroblewski\n'
                  'Jeroen Vloothuis')
        add_label('')
        notebook.append_page(tab_vbox, gtk.Label(_('Authors')))

        vbox.show_all()
        about.run()
        about.destroy()


# vim:sw=4:et:ai
