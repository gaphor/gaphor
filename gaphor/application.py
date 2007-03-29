"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

import gtk
import pkg_resources
from zope import component
from gaphor.interfaces import IService

import gaphor.ui
from gaphor.ui import mainwindow, load_accel_map, save_accel_map

class _Application(object):

    def __init__(self):
        self.services = {
            'main_window': mainwindow.MainWindow(),
            'element_factory': gaphor.UML.ElementFactory()
        }
    
    def __getattr__(self, key):
        return self.services[key]

    def init(self):
        """
        Initialize the application.
        """
        load_accel_map()
        import gaphor.adapters
        import gaphor.actions
        self.load_services()
        self.main_window.construct()
        main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit())

    def load_services(self):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            #print ep, dir(ep)
            log.debug('found entry point service.%s' % ep.name)
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IService' % ep.name
            srv = cls()
            srv.init(self)
            print 'service', srv
            component.provideUtility(srv, IService, ep.name)

    def get_service(self, name):
        component.getUtility(IService, name)

    def run(self):
        gtk.main()

    def shutdown(self):
        save_accel_map()

# Make sure there is only one!
Application = _Application()

def restart():
    Application.shutdown()
    Application = _Application()


# vim:sw=4:et:ai
