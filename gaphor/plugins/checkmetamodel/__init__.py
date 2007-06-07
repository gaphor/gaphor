# vim:sw=4:et

import gaphor.plugin
from checkmodelgui import CheckModelWindow
from checkmodel import check_associations, check_attributes

class CheckMetamodelAction(gaphor.plugin.Action):

    def execute(self):
        print 'CheckMetamodelAction'
        # TODO: override checkmodel.report
        cw = CheckModelWindow()
        cw.construct()
        self.window.add_transient_window(cw)
        cw.run()
