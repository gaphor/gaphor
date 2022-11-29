import importlib.resources
from pathlib import Path
from typing import NamedTuple

from gi.repository import GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.babel import translate_model
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, SessionCreated
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
        gettext("An empty model."),
        "org.gaphor.Gaphor",
        "UML",
        "blank.gaphor",
    ),
    ModelTemplate(
        gettext("UML"),
        gettext("A Unified Modeling Language template/example."),
        "UML",
        "UML",
        "uml.gaphor",
    ),
    ModelTemplate(
        gettext("SysML"),
        gettext("Systems Modeling template"),
        "SysML",
        "SysML",
        "sysml.gaphor",
    ),
    ModelTemplate(
        gettext("RAAML"),
        gettext("Risk Analysis Assessment template."),
        "RAAML",
        "RAAML",
        "raaml.gaphor",
    ),
    ModelTemplate(
        gettext("C4 Model"),
        gettext("Layered C4 Model template."),
        "C4Model",
        "C4Model",
        "c4model.gaphor",
    ),
]


def new_builder(ui_file):
    builder = Gtk.Builder()
    ui_file = f"{ui_file}.glade" if Gtk.get_major_version() == 3 else f"{ui_file}.ui"
    builder.add_from_string(translated_ui_string("gaphor.ui", ui_file))
    return builder


class Greeter(Service, ActionProvider):
    def __init__(self, application, event_manager, recent_manager=None):
        self.templates = None
        self.application = application
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()
        self.greeter: Gtk.Window = None
        self.action_bar: Gtk.ActionBar = None
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

        listbox = builder.get_object("greeter-recent-files")
        listbox.connect("row-activated", self._on_recent_file_activated)
        for widget in self.create_recent_files():
            listbox.insert(widget, -1)

        self.action_bar = builder.get_object("action-bar")

        self.templates = builder.get_object("templates")
        self.templates.connect("row-activated", self._on_template_activated)
        for widget in self.create_templates():
            self.templates.insert(widget, -1)

        self.greeter = builder.get_object("greeter")
        self.greeter.set_application(self.gtk_app)
        if Gtk.get_major_version() == 3:
            self.greeter.connect("delete-event", self._on_window_close_request)
        else:
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
            builder = new_builder("greeter-recent-file")
            filename, _host = GLib.filename_from_uri(item.get_uri())
            builder.get_object("name").set_text(str(Path(filename).stem))
            builder.get_object("filename").set_text(
                item.get_uri_display().replace(str(Path.home()), "~")
            )
            row = builder.get_object("greeter-recent-file")
            row.filename = filename
            yield row

    def create_templates(self):
        for template in TEMPLATES:
            builder = new_builder("greeter-model-template")
            builder.get_object("name").set_text(template.name)
            builder.get_object("description").set_text(template.description)
            if Gtk.get_major_version() == 3:
                builder.get_object("icon").set_from_icon_name(
                    template.icon, Gtk.IconSize.DIALOG
                )
            else:
                builder.get_object("icon").set_from_icon_name(template.icon)
            child = builder.get_object("model-template")
            child.filename = template.filename
            child.lang = template.lang
            yield child

    @event_handler(SessionCreated, ActiveSessionChanged)
    def on_session_created(self, _event=None):
        self.close()

    def _on_recent_file_activated(self, _listbox, row):
        filename = row.filename
        self.application.new_session(filename=filename)
        self.close()

    def _on_template_activated(self, _listbox, child):
        filename: Path = (
            importlib.resources.files("gaphor") / "templates" / child.filename
        )
        translated_model = translate_model(filename)
        session = self.application.new_session(template=translated_model)
        session.get_service("properties").set("modeling-language", child.lang)
        self.close()

    def _on_window_close_request(self, window, event=None):
        self.close()
        return False
