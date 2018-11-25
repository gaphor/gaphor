"""About and help services. (help browser anyone?)"""

import os
from builtins import object
from logging import getLogger

import pkg_resources
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from zope.interface import implementer

from gaphor.application import Application
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider


@implementer(IService, IActionProvider)
class HelpService(object):

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

    main_window = inject("main_window")
    logger = getLogger("HelpService")

    def __init__(self):
        pass

    def init(self, app):
        self.logger.info("Starting")
        self.action_group = build_action_group(self)

    def shutdown(self):
        self.logger.info("Shutting down")

    @action(name="help-about", stock_id="gtk-about")
    def about(self):
        logo_file = os.path.join(
            pkg_resources.get_distribution("gaphor").location,
            "gaphor",
            "ui",
            "pixmaps",
            "logo.png",
        )
        logo = GdkPixbuf.Pixbuf.new_from_file(logo_file)
        version = Application.distribution.version
        about = Gtk.Dialog.new()
        about.set_title(_("About Gaphor"))
        about.set_modal(True)
        about.set_transient_for(self.main_window.window)
        about.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        about.set_default_response(Gtk.ResponseType.OK)
        vbox = about.vbox

        image = Gtk.Image()
        image.set_from_pixbuf(logo)
        vbox.pack_start(image, True, True, 0)

        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(4)
        notebook.set_tab_pos(Gtk.PositionType.BOTTOM)
        vbox.pack_start(notebook, True, True, 0)

        tab_vbox = Gtk.VBox()

        def add_label(text, padding_x=0, padding_y=0):
            label = Gtk.Label(label=text)
            label.set_property("use-markup", True)
            label.set_padding(padding_x, padding_y)
            label.set_justify(Gtk.Justification.CENTER)
            tab_vbox.pack_start(label, True, True, 0)

        add_label('<span weight="bold">version %s</span>' % version)
        add_label('<span variant="smallcaps">UML Modeling tool for GNOME</span>', 8, 8)
        add_label(
            '<span size="small">Copyright (c) 2001-2007 Arjan J. Molenaar</span>', 8, 8
        )

        notebook.append_page(tab_vbox, Gtk.Label(label=_("About")))

        tab_vbox = Gtk.VBox()

        add_label(
            "This software is published\n"
            "under the terms of the\n"
            '<span weight="bold">GNU General Public License v2</span>.\n'
            "See the COPYING file for details.",
            0,
            8,
        )
        notebook.append_page(tab_vbox, Gtk.Label(label=_("License")))

        tab_vbox = Gtk.VBox()

        add_label(
            "Gaphor is written by:\n"
            "Arjan Molenaar\n"
            "Artur Wroblewski\n"
            "Jeroen Vloothuis"
        )
        add_label("")
        notebook.append_page(tab_vbox, Gtk.Label(label=_("Authors")))

        vbox.show_all()
        about.run()
        about.destroy()


# vim:sw=4:et:ai
