import importlib.resources
from pathlib import Path
from typing import NamedTuple

from gi.repository import Gdk, GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.event import ActiveSessionChanged, SessionCreated
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui import APPLICATION_ID, HOME


def new_builder(ui_file):
    builder = Gtk.Builder()
    ui_file = f"{ui_file}.glade" if Gtk.get_major_version() == 3 else f"{ui_file}.ui"
    builder.add_from_string(translated_ui_string("gaphor.ui", ui_file))
    return builder


class Greeter(Service, ActionProvider):
    def __init__(self, application, event_manager, recent_manager=None):
        self.application = application
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()
        self.greeter = None
        self.stack = None
        self.gtk_app = None
        event_manager.subscribe(self.on_session_created)

    def init(self, gtk_app):
        self.gtk_app = gtk_app

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_session_created)
        if self.greeter:
            self.greeter.destroy()
        self.gtk_app = None

    def open(self, stack_name="recent-files") -> None:
        if self.greeter and self.stack:
            self.stack.set_visible_child_name(stack_name)
            self.greeter.present()
            return

        builder = new_builder("greeter")

        listbox = builder.get_object("greeter-recent-files")
        listbox.connect("row-activated", self._on_recent_file_activated)
        for widget in self.create_recent_files():
            if Gtk.get_major_version() == 3:
                listbox.add(widget)
            else:
                listbox.append(widget)

        templates = builder.get_object("templates")
        templates.connect("child-activated", self._on_template_activated)
        for widget in self.create_templates():
            if Gtk.get_major_version() == 3:
                templates.add(widget)
            else:
                templates.append(widget)
        flowbox_add_hover_support(templates)
        self.templates = templates

        self.stack = builder.get_object("stack")
        self.stack.set_visible_child_name(stack_name)

        self.greeter = builder.get_object("greeter")
        self.greeter.set_application(self.gtk_app)
        if Gtk.get_major_version() == 3:
            self.greeter.connect("delete-event", self._on_window_delete)
        else:
            ...  # TODO: Handle window close in GTK4

        self.greeter.show()
        templates.unselect_all()

    def close(self):
        if self.greeter:
            self.greeter.destroy()
            self.greeter = None
            self.stack = None

    @action(name="app.recent-files", shortcut="<Primary>n")
    def recent_files(self):
        self.open("recent-files" if any(self.create_recent_files()) else "new-model")

    @action(name="app.new-model")
    def new_model(self):
        self.open("new-model")

    def create_recent_files(self):
        for item in self.recent_manager.get_items():
            if APPLICATION_ID in item.get_applications() and item.exists():
                builder = new_builder("greeter-recent-file")
                filename, _host = GLib.filename_from_uri(item.get_uri())
                builder.get_object("name").set_text(str(Path(filename).stem))
                builder.get_object("filename").set_text(
                    item.get_uri_display().replace(HOME, "~")
                )
                row = builder.get_object("greeter-recent-file")
                row.filename = filename
                yield row

    def create_templates(self):
        for template in TEMPLATES:
            builder = new_builder("greeter-model-template")
            builder.get_object("template-name").set_text(template.name)
            builder.get_object("template-icon").set_from_icon_name(
                template.icon, Gtk.IconSize.DIALOG
            )
            child = builder.get_object("model-template")
            child.filename = template.filename
            yield child

    @event_handler(SessionCreated, ActiveSessionChanged)
    def on_session_created(self, _event=None):
        self.close()

    def _on_recent_file_activated(self, _listbox, row):
        filename = row.filename
        self.application.new_session(filename=filename)
        self.close()

    def _on_template_activated(self, _flowbox, child):
        filename: Path = (
            importlib.resources.files("gaphor") / "templates" / child.filename
        )
        self.application.new_session(template=filename)
        self.close()

    def _on_window_delete(self, window, event):
        self.close()


class ModelTemplate(NamedTuple):
    name: str
    icon: str
    filename: str


TEMPLATES = [
    ModelTemplate(gettext("Generic"), "org.gaphor.Gaphor", "blank.gaphor"),
    ModelTemplate(gettext("C4 Model"), "org.gaphor.Gaphor", "c4model.gaphor"),
]


if Gtk.get_major_version() == 3:

    def flowbox_add_hover_support(flowbox):
        flowbox.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        hover_child: Gtk.Widget = None

        def hover(widget, event):
            nonlocal hover_child
            child = widget.get_child_at_pos(event.x, event.y)
            if hover_child and child is not hover_child:
                hover_child.unset_state_flags(Gtk.StateFlags.PRELIGHT)
            if child:
                child.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
            hover_child = child

        def unhover(widget, event):
            if hover_child:
                hover_child.unset_state_flags(Gtk.StateFlags.PRELIGHT)

        flowbox.connect("motion-notify-event", hover)
        flowbox.connect("leave-notify-event", unhover)

else:

    def flowbox_add_hover_support(flowbox):
        pass
