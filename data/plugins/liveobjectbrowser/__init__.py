# vim:sw=4:et

import gaphor.plugin
from browser import Browser
import gaphor

class LiveObjectBrowserAction(gaphor.plugin.Action):

    def execute(self):
        self.browser = Browser("resource", gaphor.resource('ElementFactory').select())
