"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

import pkg_resources
from zope import component
from gaphor.interfaces import IService

import gaphor.UML

# Backwards compat
from gaphor import resource

class _Application(object):

    # interface.implements(IApplication)
    
    def __init__(self):
        self.services = {
            'element_factory': gaphor.UML.ElementFactory()
        }
    
#    def __getattr__(self, key):
#        return self.services[key]

    def init(self):
        """
        Initialize the application.
        """
        #import gaphor.adapters
        #import gaphor.actions
        self.load_services()

    def load_services(self):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        services = []
        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            #print ep, dir(ep)
            log.debug('found entry point service.%s' % ep.name)
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IService' % ep.name
            srv = cls()
            services.append((ep.name, srv))

        for name, srv in services:
            log.debug('initializing service.%s' % name)
            component.provideUtility(srv, IService, name)
            srv.init(self)

    distribution = property(lambda s: pkg_resources.get_distribution('gaphor'),
                            doc='Get the PkgResources distribution for Gaphor')

    def get_service(self, name):
        return component.getUtility(IService, name)

    def run(self):
        import gtk
        gtk.main()

    def shutdown(self):
        pass # for each IService: shutdown

# Make sure there is only one!
Application = _Application()

def restart():
    Application.shutdown()
    Application = _Application()


# vim:sw=4:et:ai
