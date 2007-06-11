"""
This plugin extends Gaphor with XMI export functionality.
"""

__plugin__ = "XMI Export"
__version__ = "0.1"
__author__ = "Jeroen Vloothuis"
__description__ = 'This plugin extends Gaphor with XMI export functionality.'

import gtk
from zope import interface, component
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider

import exportmodel

class XMIExport(object):

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    gui_manager = inject('gui_manager')

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
    
    def __init__(self):
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    @action(name='file-export-xmi', label=_('Export to XMI'),
            tooltip=_('Export model to XMI (XML Model Interchange) format'))
    def execute(self):
        filename = self.gui_manager.main_window.get_filename()
        if filename:
            filename = filename.replace('.gaphor', '.xmi')
        else:
            filename = 'model.xmi'

        filesel = gtk.FileChooserDialog(title='Export model to XMI file',
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        filesel.set_current_name(filename)

        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if response == gtk.RESPONSE_OK:
            if filename and len(filename) > 0:
                log.debug('Exporting XMI model to: %s' % filename)
                export = exportmodel.XMIExport(self.element_factory)
                try:
                    export.export(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))


# vim:sw=4:et
