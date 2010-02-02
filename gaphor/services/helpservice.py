"""
About and help services. (help browser anyone?)
"""


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

    gui_manager = inject('gui_manager')

    def __init__(self):
        pass

    def init(self, app):
        self.action_group = build_action_group(self)

    def shutdown(self):
        pass

    @action(name='help-about', stock_id='gtk-about')
    def about(self):
        logo_file =  os.path.join(pkg_resources.get_distribution('gaphor').location, 'gaphor', 'ui', 'pixmaps', 'logo.png')
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        version = Application.distribution.version
        about = gtk.Dialog("About Gaphor", self.gui_manager.main_window.window, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
        about.set_default_response(gtk.RESPONSE_OK)
        vbox = about.vbox

        image = gtk.Image()
        image.set_from_pixbuf(logo)
        vbox.pack_start(image)

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        #notebook.set_show_border(False)
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

        #add_label('<span size="xx-large" weight="bold">Gaphor</span>')
        add_label('<span weight="bold">version %s</span>' % version)
        add_label('<span variant="smallcaps">UML Modeling tool for GNOME</span>', 8, 8)
        add_label('<span size="small">Copyright (c) 2001-2007 Arjan J. Molenaar</span>', 8, 8)
        #vbox.pack_start(gtk.HSeparator())
        notebook.append_page(tab_vbox, gtk.Label('About'))

        tab_vbox = gtk.VBox()
        
        add_label('This software is published\n'
                  'under the terms of the\n'
                  '<span weight="bold">GNU General Public License v2</span>.\n'
                  'See the COPYING file for details.', 0, 8)
        notebook.append_page(tab_vbox, gtk.Label('License'))

        tab_vbox = gtk.VBox()
        
        add_label('Gaphor is written by:\n'
                  'Arjan Molenaar\n'
                  'Artur Wroblewski\n'
                  'Jeroen Vloothuis')
        add_label('')
        notebook.append_page(tab_vbox, gtk.Label('Authors'))

        vbox.show_all()
        about.run()
        about.destroy()


# vim:sw=4:et:ai
