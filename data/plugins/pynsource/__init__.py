# vim:sw=4:et:

import gaphor.plugin

from pynsource import PythonToJava, PySourceAsJava
from pynsourcewindow import PyNSourceWindow

class PyNSourceAction(gaphor.plugin.Action):

    def __init__(self):
        gaphor.plugin.Action.__init__(self)
        self.win = None

    def execute(self):
        if not self.win or self.win.get_state() == self.win.STATE_CLOSED:
            self.win = PyNSourceWindow(self.get_window())
            self.win.construct()
        else:
            self.win.show()

if __name__ in ('__main__', '__builtin__'):
    print 'Loading...'
    import gtk
    win = PyNSourceWindow()
    win.construct()
    win.get_window().connect('destroy', lambda e: gtk.main_quit())
    gtk.main()
