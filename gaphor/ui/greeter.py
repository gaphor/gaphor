import importlib.resources
from pathlib import Path
from typing import NamedTuple

from gi.repository import Adw, GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.application import distribution
from gaphor.babel import translate_model
from gaphor.core import event_handler
from gaphor.event import SessionCreated
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui import APPLICATION_ID


class ModelTemplate(NamedTuple):
    name: str
    description: str
    icon: str
    lang: str
    filename: str


TEMPLATES = [
    ModelTemplate(
        gettext("Generic"),
        gettext("An empty model"),
        "org.gaphor.Gaphor",
        "UML",
        "blank.gaphor",
    ),
    ModelTemplate(
        gettext("UML"),
        gettext("Unified Modeling Language template"),
        "UML",
        "UML",
        "uml.gaphor",
    ),
    ModelTemplate(
        gettext("SysML"),
        gettext("Systems Modeling Language template"),
        "SysML",
        "SysML",
        "sysml.gaphor",
    ),
    ModelTemplate(
        gettext("RAAML"),
        gettext("Risk Analysis and Assessment Modeling Language template"),
        "RAAML",
        "RAAML",
        "raaml.gaphor",
    ),
    ModelTemplate(
        gettext("C4 Model"),
        gettext("Layered C4 Model template"),
        "C4Model",
        "C4Model",
        "c4model.gaphor",
    ),
]


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", f"{ui_file}.ui"))
    return builder


class Greeter(Service, ActionProvider):
    def __init__(self, application, event_manager, recent_manager=None):
        self.application = application
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()
        self.greeter: Gtk.Window = None
        self.gtk_app: Gtk.Application = None
        event_manager.subscribe(self.on_session_created)

    def init(self, gtk_app):
        self.gtk_app = gtk_app

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_session_created)

        if self.greeter:
            self.greeter.destroy()
        self.gtk_app = None

    def open(self) -> None:
        if self.greeter:
            self.greeter.present()
            return

        builder = new_builder("greeter")

        self.greeter = builder.get_object("greeter")
        self.greeter.set_application(self.gtk_app)
        if ".dev" in distribution().version:
            self.greeter.get_style_context().add_class("devel")

        listbox = builder.get_object("recent-files")
        templates = builder.get_object("templates")

        if any(self.query_recent_files()):
            for widget in self.create_recent_files():
                listbox.add(widget)
        else:
            builder.get_object("recent-files").hide()

        for widget in self.create_templates():
            templates.add(widget)

        self.greeter.connect("close-request", self._on_window_close_request)
        self.greeter.show()

    def close(self):
        if self.greeter:
            self.greeter.destroy()
            self.greeter = None

    @action(name="app.new-model", shortcut="<Primary>n")
    def new_model(self):
        self.open()

    def query_recent_files(self):
        for item in self.recent_manager.get_items():
            if APPLICATION_ID in item.get_applications() and item.exists():
                yield item

    def create_recent_files(self):
        for item in self.query_recent_files():
            filename, _host = GLib.filename_from_uri(item.get_uri())
            row = Adw.ActionRow.new()
            row.set_activatable(True)
            row.set_title(str(Path(filename).stem))
            row.set_subtitle(item.get_uri_display().replace(str(Path.home()), "~"))
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            row.connect("activated", self._on_recent_file_activated)
            row.filename = filename
            yield row

    def create_templates(self):
        for template in TEMPLATES:
            row = Adw.ActionRow.new()
            row.set_activatable(True)
            row.set_title(template.name)
            row.set_subtitle(template.description)
            image = Gtk.Image.new_from_icon_name(template.icon)
            image.set_pixel_size(36)
            row.add_prefix(image)
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            row.connect("activated", self._on_template_activated)

            row.filename = template.filename
            row.lang = template.lang
            yield row

    @event_handler(SessionCreated)
    def on_session_created(self, _event=None):
        self.close()

    def _on_recent_file_activated(self, row):
        filename = row.filename
        self.application.new_session(filename=filename)
        self.close()

    def _on_template_activated(self, child):
        filename = importlib.resources.files("gaphor") / "templates" / child.filename
        translated_model = translate_model(filename)
        session = self.application.new_session(template=translated_model)
        session.get_service("properties").set("modeling-language", child.lang)
        self.close()

    def _on_window_close_request(self, window, event=None):
        self.close()
        return False
