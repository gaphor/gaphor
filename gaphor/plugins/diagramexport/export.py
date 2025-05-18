from __future__ import annotations

from pathlib import Path

from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, event_handler, gettext
from gaphor.diagram.event import DiagramClosed, DiagramOpened
from gaphor.diagram.export import (
    escape_filename,
    save_eps,
    save_pdf,
    save_png,
    save_svg,
)
from gaphor.event import ActionEnabled
from gaphor.plugins.diagramexport.exportall import export_all
from gaphor.ui.filedialog import save_file_dialog


class DiagramExport(Service, ActionProvider):
    """Service for exporting diagrams as images (SVG, PNG, PDF)."""

    def __init__(
        self,
        event_manager,
        diagrams=None,
        export_menu=None,
        main_window=None,
        element_factory=None,
    ):
        super().__init__()
        self.event_manager = event_manager
        self.diagrams = diagrams
        self.export_menu = export_menu
        self.main_window = main_window
        if export_menu:
            export_menu.add_actions(self)
        self.filename: Path = Path("export").absolute()
        self.factory = element_factory
        event_manager.subscribe(self.on_diagram_opened_or_closed)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_diagram_opened_or_closed)
        if self.export_menu:
            self.export_menu.remove_actions(self)

    async def save_dialog(self, diagram, title, ext, mime_type, handler):
        dot_ext = f".{ext}"
        filename = self.filename.with_name(
            escape_filename(diagram.name) or "export"
        ).with_suffix(dot_ext)

        new_filename = await save_file_dialog(
            title,
            filename,
            parent=self.main_window.window,
            filters=[
                (
                    gettext("All {ext} Files").format(ext=ext.upper()),
                    dot_ext,
                    mime_type,
                )
            ],
        )
        if new_filename:
            self.filename = new_filename
            handler(new_filename, diagram)

    @action(
        name="file-export-svg",
        label=gettext("Export as SVG"),
        tooltip=gettext("Export diagram as SVG"),
    )
    async def save_svg_action(self):
        diagram = self.diagrams.get_current_diagram()
        await self.save_dialog(
            diagram, gettext("Export diagram as SVG"), "svg", "image/svg+xml", save_svg
        )

    @action(
        name="file-export-png",
        label=gettext("Export as PNG"),
        tooltip=gettext("Export diagram as PNG"),
    )
    async def save_png_action(self):
        diagram = self.diagrams.get_current_diagram()
        await self.save_dialog(
            diagram, gettext("Export diagram as PNG"), "png", "image/png", save_png
        )

    @action(
        name="file-export-pdf",
        label=gettext("Export as PDF"),
        tooltip=gettext("Export diagram as PDF"),
    )
    async def save_pdf_action(self):
        diagram = self.diagrams.get_current_diagram()
        await self.save_dialog(
            diagram,
            gettext("Export diagram as PDF"),
            "pdf",
            "application/pdf",
            save_pdf,
        )

    @action(
        name="file-export-eps",
        label=gettext("Export as EPS"),
        tooltip=gettext("Export diagram as Encapsulated PostScript"),
    )
    async def save_eps_action(self):
        diagram = self.diagrams.get_current_diagram()
        await self.save_dialog(
            diagram,
            gettext("Export diagram as EPS"),
            "eps",
            "application/postscript",
            save_eps,
        )

    @action(
        name="all-export-svg",
        label=gettext("Export all diagrams as SVG"),
        tooltip=gettext("Export all diagrams as SVG diagrams in a specifieddirectory"),
    )
    def export_all_svg_action(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title(gettext("Export all diagrams"))

        def response(dialog, result):
            if result.had_error():
                return

            folder = dialog.select_folder_finish(result).get_path()
            export_all(self.factory, folder, save_svg, "svg")

        dialog.select_folder(callback=response)

    @action(
        name="all-export-png",
        label=gettext("Export all diagrams as PNG"),
        tooltip=gettext("Export all diagrams as PNG diagrams in a specifieddirectory"),
    )
    def export_all_png_action(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title(gettext("Export all diagrams"))

        def response(dialog, result):
            if result.had_error():
                return

            folder = dialog.select_folder_finish(result).get_path()
            export_all(self.factory, folder, save_png, "png")

        dialog.select_folder(callback=response)

    @action(
        name="all-export-pdf",
        label=gettext("Export all diagrams as PDF"),
        tooltip=gettext("Export all diagrams as PDF diagrams in a specifieddirectory"),
    )
    def export_all_pdf_action(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title(gettext("Export all diagrams"))

        def response(dialog, result):
            if result.had_error():
                return

            folder = dialog.select_folder_finish(result).get_path()
            export_all(self.factory, folder, save_pdf, "pdf")

        dialog.select_folder(callback=response)

    @action(
        name="all-export-eps",
        label=gettext("Export all diagrams as EPS"),
        tooltip=gettext("Export all diagrams as EPS diagrams in a specifieddirectory"),
    )
    def export_all_eps_action(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title(gettext("Export all diagrams"))

        def response(dialog, result):
            if result.had_error():
                return

            folder = dialog.select_folder_finish(result).get_path()
            export_all(self.factory, folder, save_eps, "eps")

        dialog.select_folder(callback=response)

    @event_handler(DiagramOpened, DiagramClosed)
    def on_diagram_opened_or_closed(self, event: DiagramOpened | DiagramClosed):
        enabled = (
            isinstance(event, DiagramOpened) or self.diagrams.get_current_diagram()
        )

        for action_name in (
            "win.file-export-svg",
            "win.file-export-png",
            "win.file-export-pdf",
            "win.file-export-eps",
        ):
            self.event_manager.handle(ActionEnabled(action_name, enabled))
