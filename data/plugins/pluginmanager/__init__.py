# vim:sw=4:et

import gaphor.plugin
from pluginmanager import PluginManagerWindow

class PluginManagerAction(gaphor.plugin.Action):

    def execute(self):
        #print 'CheckMetamodelAction'
        # TODO: override checkmodel.report
        cw = PluginManagerWindow()
        cw.construct()
        self.window.add_transient_window(cw)
