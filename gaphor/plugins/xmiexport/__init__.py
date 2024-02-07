"""This plugin extends Gaphor with XMI export functionality."""

import logging
from pathlib import Path

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.plugins.xmiexport import exportmodel
from gaphor.ui.filedialog import save_file_dialog

logger = logging.getLogger(__name__)


class XMIExport(Service, ActionProvider):
    def __init__(self, element_factory, file_manager, export_menu):
        self.element_factory = element_factory
        self.file_manager = file_manager
        export_menu.add_actions(self)

    def shutdown(self):
        pass

    @action(
        name="file-export-xmi",
        label=gettext("Export as XMI"),
        tooltip=gettext("Export model as XMI (XML Model Interchange) format"),
    )
    def execute(self):
        def handler(filename):
            logger.debug(f"Exporting XMI model to: {filename}")
            export = exportmodel.XMIExport(self.element_factory)
            try:
                export.export(filename)
            except Exception as e:
                logger.error(f"Error while saving model to file {filename}: {e}")

        filename = (
            self.file_manager.filename.with_suffix(".xmi")
            if self.file_manager.filename
            else Path("model.xmi")
        )
        save_file_dialog(
            gettext("Export model as XMI file"),
            filename,
            handler,
            filters=[(gettext("All XMI Files"), ".xmi", "text/xml")],
        )
