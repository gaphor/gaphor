# vim:sw=4:et

import gtk
from exportmodel import XMIExport        
from gaphor.plugin import Action


class XMIExportAction(Action):

    def execute(self):
        filesel = gtk.FileSelection('Export model to XMI file')
        filesel.set_modal(True)
        filename = self.get_window().get_filename()
        if filename:
            filename = filename.replace('.gaphor', '.xmi')
        else:
            filename = 'model.xmi'
        filesel.set_filename(filename)

        response = filesel.run()
        filesel.hide()
        if response == gtk.RESPONSE_OK:
            filename = filesel.get_filename()
            if filename and len(filename) > 0:
                #self.filename = filename
                log.debug('Exporting XMI model to: %s' % filename)
                export = XMIExport()
                try:
                    export.export(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))

