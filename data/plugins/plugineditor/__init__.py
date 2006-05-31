# vim:sw=4:et

import gaphor.plugin
from plugineditor import PluginEditorWindow

class PluginEditorAction(gaphor.plugin.Action):

    def execute(self):
        #print 'CheckMetamodelAction'
        # TODO: override checkmodel.report
        cw = PluginEditorWindow()
        cw.construct()
        self.window.add_transient_window(cw)
