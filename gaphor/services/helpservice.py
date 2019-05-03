"""About and help services. (help browser anyone?)"""

import os

import pkg_resources
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from zope.interface import implementer

from gaphor import __version__
from gaphor.core import _, inject, action, build_action_group
from gaphor.abc import ActionProvider
from gaphor.interfaces import IService


@implementer(IService)
class HelpService(ActionProvider):

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

    def __init__(self):
        pass

    def init(self, app):
        self.action_group = build_action_group(self)

    def shutdown(self):
        pass

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
        version = __version__
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

        add_label('<span weight="bold">Version %s</span>' % version)
        add_label(
            '<span variant="smallcaps">Gaphor is the simple modeling tool written in Python</span>',
            8,
            8,
        )
        add_label(
            '<span size="small">Copyright (c) 2001-2019 Arjan J. Molenaar and Dan Yeaw</span>',
            8,
            8,
        )

        notebook.append_page(tab_vbox, Gtk.Label(label=_("About")))

        tab_vbox = Gtk.VBox()

        add_label(
            "This software is published\n"
            "under the terms of the\n"
            '<span weight="bold">Apache Software License v2</span>.\n'
            "See the LICENSE.txt file for details.",
            0,
            8,
        )
        notebook.append_page(tab_vbox, Gtk.Label(label=_("License")))

        tab_vbox = Gtk.VBox()

        add_label(
            "Thanks to all the wonderful people that have contributed:\n\n"
            "Arjan Molenaar\n"
            "Artur Wroblewski\n"
            "Jeroen Vloothuis\n"
            "Dan Yeaw\n"
            "Enno Groeper\n"
            "Adam Boduch\n"
            "Jordi Mallach\n"
            "Ygor Mutti\n"
            "Alexis Howells\n"
            "Encolpe Degoute\n"
            "Melis Dogan"
        )
        add_label("")
        notebook.append_page(tab_vbox, Gtk.Label(label=_("Contributors")))

        vbox.show_all()
        about.run()
        about.destroy()
