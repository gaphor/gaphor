# vim:sw=4:et

import gaphor.plugin
from gaphor.core import inject
from browser import Browser
import gaphor

class LiveObjectBrowserAction(gaphor.plugin.Action):

    element_factory = inject('element_factory')

    def execute(self):
        browser = Browser()
        browser.construct("resource", element_factory.lselect())
        self.window.add_transient_window(browser)
