"""GUI service for exporting an HTML model report."""

from __future__ import annotations

from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.plugins.htmlreport.generator import generate_report


class HtmlReportExport(Service, ActionProvider):
    """Service for exporting an HTML model report."""

    def __init__(self, event_manager, export_menu=None, element_factory=None):
        super().__init__()
        self.export_menu = export_menu
        self.factory = element_factory
        if export_menu:
            export_menu.add_actions(self)

    def shutdown(self):
        if self.export_menu:
            self.export_menu.remove_actions(self)

    @action(
        name="export-html-report",
        label=gettext("Export as HTML Report"),
        tooltip=gettext("Export model as a navigable HTML report"),
    )
    def export_html_report_action(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title(gettext("Export HTML Report"))

        def response(dialog, result):
            if result.had_error():
                return

            folder = dialog.select_folder_finish(result).get_path()
            generate_report(self.factory, folder)

        dialog.select_folder(callback=response)
