# vim:sw=4:et

print 'plugin',__file__

import gaphor.plugin

class CheckMetamodelAction(gaphor.plugin.Action):

    def init(self, window):
        self._window = window

    def execute(self):
        print 'UMLSanityCheck'

