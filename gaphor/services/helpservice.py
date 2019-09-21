"""About and help services. (help browser anyone?)"""

import os

import importlib_metadata
from gi.repository import GdkPixbuf
from gi.repository import Gtk


from gaphor import __version__
from gaphor.core import _, action, build_action_group
from gaphor.abc import Service, ActionProvider


class HelpService(Service, ActionProvider):

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

    def __init__(self, main_window):
        self.main_window = main_window
        self.action_group = build_action_group(self)

    def shutdown(self):
        pass

    @action(name="help-about", label=_("About Gaphor"), icon_name="help-about")
    def about(self):
        logo_file = importlib_metadata.distribution("gaphor").locate_file(
            "gaphor/ui/pixmaps/gaphor-96x96.png"
        )
        logo = GdkPixbuf.Pixbuf.new_from_file(str(logo_file))
        about = Gtk.AboutDialog.new()
        about.set_logo(logo)
        about.set_title("About Gaphor")
        about.set_program_name("Gaphor")
        about.set_comments("Gaphor is the simple modeling tool written in Python")
        about.set_version(str(__version__))
        about.set_copyright("Copyright (c) 2001-2019 Arjan J. Molenaar and Dan Yeaw")
        about.set_license(
            "This software is published under the terms of the\n"
            "Apache Software License, version 2.0.\n"
            "See the LICENSE.txt file for details."
        )
        about.set_website("https://github.com/gaphor/gaphor")
        about.set_website_label("Fork me on GitHub")
        about.set_authors(
            [
                "Arjan Molenaar, Artur Wroblewski,",
                "Jeroen Vloothuis, Dan Yeaw, ",
                "Enno Groeper, Adam Boduch, ",
                "Alexis Howells, Melis Doğan",
            ]
        )
        about.set_translator_credits(
            "Jordi Mallach (ca), " "Antonin Delpeuch (fr), " "Ygor Mutti (pt_BR)"
        )
        about.set_transient_for(self.main_window.window)
        about.show_all()
        about.run()
        about.destroy()
