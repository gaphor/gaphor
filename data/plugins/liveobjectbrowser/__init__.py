# vim:sw=4:et

import gaphor.plugin
from browser import Browser
import gaphor

class LiveObjectBrowserAction(gaphor.plugin.Action):

    def execute(self):
        browser = Browser()
        browser.construct("resource", gaphor.resource('ElementFactory').select())
        self.window.add_transient_window(browser)
