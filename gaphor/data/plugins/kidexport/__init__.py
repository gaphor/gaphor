# vim:sw=4:et

import gtk
from exportmodel import KidExport        
from gaphor.plugin import Action


class KidExportAction(Action):

    def execute(self):
        filename = self.get_window().get_filename()
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
                export = KidExport()
                try:
                    export.export(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))

