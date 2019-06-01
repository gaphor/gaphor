"""
This plugin extends Gaphor with XMI export functionality.
"""

import logging

from gaphor.core import _, inject, action, build_action_group
from gaphor.abc import Service, ActionProvider
from gaphor.plugins.xmiexport import exportmodel
from gaphor.ui.filedialog import FileDialog

logger = logging.getLogger(__name__)


class XMIExport(Service, ActionProvider):

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="file">
            <menu action="file-export">
              <menuitem action="file-export-xmi" />
            </menu>
          </menu>
        </menubar>
      </ui>"""

    def __init__(self, element_factory, file_manager):
        self.element_factory = element_factory
        self.file_manager = file_manager
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    @action(
        name="file-export-xmi",
        label=_("Export to XMI"),
        tooltip=_("Export model to XMI (XML Model Interchange) format"),
    )
    def execute(self):
        filename = self.file_manager.filename
        if filename:
            filename = filename.replace(".gaphor", ".xmi")
        else:
            filename = "model.xmi"

        file_dialog = FileDialog(
            _("Export model to XMI file"), action="save", filename=filename
        )

        filename = file_dialog.selection

        if filename and len(filename) > 0:
            logger.debug("Exporting XMI model to: %s" % filename)
            export = exportmodel.XMIExport(self.element_factory)
            try:
                export.export(filename)
            except Exception as e:
                logger.error("Error while saving model to file %s: %s" % (filename, e))


# vim:sw=4:et
