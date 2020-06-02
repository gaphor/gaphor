"""
This plugin extends Gaphor with XMI export functionality.
"""

import logging

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.plugins.xmiexport import exportmodel
from gaphor.ui.filedialog import FileDialog

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
        label=gettext("Export to XMI"),
        tooltip=gettext("Export model to XMI (XML Model Interchange) format"),
    )
    def execute(self):
        filename = self.file_manager.filename
        filename = filename.replace(".gaphor", ".xmi") if filename else "model.xmi"
        file_dialog = FileDialog(
            gettext("Export model to XMI file"), action="save", filename=filename
        )

        filename = file_dialog.selection

        if filename and len(filename) > 0:
            logger.debug(f"Exporting XMI model to: {filename}")
            export = exportmodel.XMIExport(self.element_factory)
            try:
                export.export(filename)
            except Exception as e:
                logger.error(f"Error while saving model to file {filename}: {e}")
