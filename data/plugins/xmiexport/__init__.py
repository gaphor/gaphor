# vim:sw=4:et

import gtk
from exportmodel import XMIExport        
from gaphor.plugin import Action


class XMIExportAction(Action):

    def execute(self):
        filename = self.get_window().get_filename()
        if filename:
            filename = filename.replace('.gaphor', '.xmi')
        else:
            filename = 'model.xmi'

        if gtk.pygtk_version < (2, 4, 0):
            filesel = gtk.FileSelection('Export model to XMI file')
            filesel.set_filename(filename)
        else:
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
                export = XMIExport()
                try:
                    export.export(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))

