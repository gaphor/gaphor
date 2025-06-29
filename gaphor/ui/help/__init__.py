"""About, preferences, and help services.

(help browser anyone?)
"""

import datetime
import logging
import sys
import textwrap
import time
from types import TracebackType

import better_exceptions
from gi.repository import Adw, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.application import distribution
from gaphor.core import action
from gaphor.event import Notification
from gaphor.i18n import gettext, translated_ui_string
from gaphor.settings import StyleVariant, settings
from gaphor.ui.selftest import system_information

logger = logging.getLogger(__name__)

better_exceptions.SUPPORTS_COLOR = False

START_TIME = time.time()


def new_builder(ui_file):
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui.help", f"{ui_file}.ui"))
    return builder


class HelpService(Service, ActionProvider):
    def __init__(self, application):
        self.application = application
        self.preferences_dialog = None

        self.exceptions: list[
            tuple[float, type[BaseException], BaseException, TracebackType | None]
        ] = []
        self._orig_excepthook = sys.excepthook
        sys.excepthook = self.excepthook

    def shutdown(self):
        sys.excepthook = self._orig_excepthook

    @property
    def window(self):
        return self.application.active_window

    @action(name="app.about")
    def about(self):
        builder = new_builder("about")
        about = builder.get_object("about")

        about.set_version(distribution().version)
        about.set_debug_info(self.create_debug_info())
        about.present(self.window)
        return about

    @action(name="app.shortcuts", shortcut="<Primary>question")
    def shortcuts(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "shortcuts.ui")
        modifier = "Meta" if sys.platform == "darwin" else "Control"
        ui = ui.replace("&lt;Primary&gt;", f"&lt;{modifier}&gt;")

        builder.add_from_string(ui)

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.present(self.window)
        return shortcuts

    def _on_style_variant_selected(self, combo_row: Adw.ComboRow, param) -> None:
        if self.application.gtk_app:
            selected = combo_row.props.selected_item
            if selected.props.string == "Dark":
                settings.style_variant = StyleVariant.DARK
            elif selected.props.string == "Light":
                settings.style_variant = StyleVariant.LIGHT
            else:
                settings.style_variant = StyleVariant.SYSTEM

    def _on_use_english_selected(self, switch_row: Adw.SwitchRow, param) -> None:
        if self.preferences_dialog:
            self.preferences_dialog.add_toast(
                Adw.Toast(
                    title=gettext("Restart Gaphor to enable language changes"),
                )
            )

    @action(name="app.preferences", shortcut="<Primary>comma")
    def preferences(self):
        builder = Gtk.Builder()
        ui = translated_ui_string("gaphor.ui.help", "preferences.ui")

        builder.add_from_string(ui)

        self.preferences_dialog = builder.get_object("preferences")

        style_variant: Adw.ComboRow = builder.get_object("style_variant")
        use_english: Adw.SwitchRow = builder.get_object("use_english")
        reset_tool_after_create: Adw.SwitchRow = builder.get_object(
            "reset_tool_after_create"
        )
        remove_unused_elements: Adw.SwitchRow = builder.get_object(
            "remove_unused_elements"
        )

        settings.bind_use_english(use_english, "active")
        use_english.connect("notify::active", self._on_use_english_selected)

        settings.bind_style_variant(style_variant, "selected")
        style_variant.connect("notify::selected-item", self._on_style_variant_selected)

        settings.bind_reset_tool_after_create(reset_tool_after_create, "active")
        settings.bind_remove_unused_elements(remove_unused_elements, "active")

        self.preferences_dialog.present(self.window)
        return self.preferences_dialog

    def create_debug_info(self):
        buffer = []

        buffer.append(system_information())
        buffer.append("\n\n")

        if not self.exceptions:
            buffer.append(gettext("No errors have been intercepted. We’re good."))
            return "".join(buffer)

        buffer.append(gettext("Errors:"))
        buffer.append("\n\n")

        def print_exception(tp, v, tb, depth=0):
            for line in better_exceptions.format_exception(tp, v, tb):
                buffer.append(textwrap.indent(line, "  " * depth + "|"))
            if issubclass(tp, BaseExceptionGroup):
                for i, sub_exc in enumerate(v.exceptions):
                    buffer.append(
                        f"{'  ' * depth}{'└─┬──' if i == 0 else '  ├──'}────────────────────────────╌┄┈\n"
                    )
                    print_exception(
                        type(sub_exc), sub_exc, sub_exc.__traceback__, depth=depth + 1
                    )
                buffer.append(
                    f"{'  ' * (depth + 1)}└─────────────────────────────╌┄┈\n"
                )
            elif depth == 0:
                buffer.append("└─────────────────────────────╌┄┈\n")

        for ts, tp, v, tb in self.exceptions:
            buffer.append(
                f"Time since application startup: {datetime.timedelta(seconds=int(ts - START_TIME))}\n"
            )
            print_exception(tp, v, tb)

            return "".join(buffer)

    def excepthook(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ):
        self.exceptions.append((time.time(), exc_type, exc_value, exc_traceback))
        logger.exception(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        if session := self.application.active_session:
            session.get_service("event_manager").handle(
                Notification(
                    gettext(
                        "An unexpected error occurred.\nPlease file an issue on GitHub and include information from Tools → Error Reports."
                    )
                )
            )
