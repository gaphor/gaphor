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
from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent
import gaphor.UML


class _Application(object):
    """
    The Gaphor application is started from the Application instance. It behaves
    as a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered as "utilities" in a global registry.

    Methods are provided that wrap zope.component's handle, adapter and
    subscription registrations. In addition to registration methods also
    unregister methods are provided. This way services can be properly
    unregistered on shutdown for example.
    """

    # interface.implements(IApplication)
    
    def __init__(self):
        self._uninitialized_services = {}
        self.globalSiteManager = component.getGlobalSiteManager()

    def init(self, services=None):
        """
        Initialize the application.
        """
        self.load_services(services)
        self.init_all_services()

    def load_services(self, services=None):
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
            if services is None or ep.name in services:
                srv = cls()
                self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        while self._uninitialized_services:
            self.init_service(self._uninitialized_services.iterkeys().next())

    def init_service(self, name):
        """
        Initialize a not yet initialized service.

        Raises ComponentLookupError if the service has nor been found
        """
        try:
            srv = self._uninitialized_services.pop(name)
        except KeyError:
            raise component.ComponentLookupError(IService, name)
        else:
            log.info('initializing service service.%s' % name)
            srv.init(self)
            self.globalSiteManager.registerUtility(srv, IService, name)
            self.handle(ServiceInitializedEvent(name, srv))
            return srv

    distribution = property(lambda s: pkg_resources.get_distribution('gaphor'),
                            doc='Get the PkgResources distribution for Gaphor')

    def get_service(self, name):
        try:
            return self.globalSiteManager.getUtility(IService, name)
        except component.ComponentLookupError:
            return self.init_service(name)

    def run(self):
        import gtk
        gtk.main()

    def shutdown(self):
        for name, srv in self.globalSiteManager.getUtilitiesFor(IService):
            srv.shutdown()
            self.handle(ServiceShutdownEvent(name, srv))
            self.globalSiteManager.unregisterUtility(srv, IService, name)

        # Re-initialize Zope's global site manager
        # (cleanup adapters and utilities):
        try:
            self.globalSiteManager.__init__('base')
        except Exception, e:
            log.error('Re-initialization of the Zope SiteManager failed', e)
        self.__init__()

    # Wrap zope.component's SiteManager methods

    def registerAdapter(self, factory, adapts=None, provides=None, name=''):
        """
        Register an adapter (factory) that adapts objects to a specific
        interface. A name can be used to distinguish between different adapters
        that adapt to the same interfaces.
        """
        self.globalSiteManager.registerAdapter(factory, adapts, provides,
                              name, event=False)

    def unregisterAdapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered adapter.
        """
        self.globalSiteManager.unregisterAdapter(factory,
                              required, provided, name)

    def registerSubscriptionAdapter(self, factory, adapts=None, provides=None):
        """
        Register a subscription adapter. See registerAdapter().
        """
        self.globalSiteManager.registerSubscriptionAdapter(factory, adapts,
                              provides, event=False)

    def unregisterSubscriptionAdapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered subscription adapter.
        """
        self.globalSiteManager.unregisterSubscriptionAdapter(factory,
                              required, provided, name)

    def registerHandler(self, factory, adapts=None):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emited through the handle() method.
        """
        self.globalSiteManager.registerHandler(factory, adapts, event=False)

    def unregisterHandler(self, factory=None, required=None):
        """
        Unregister a previously registered handler.
        """
        self.globalSiteManager.unregisterHandler(factory, required)
 
    def handle(self, *objects):
        """
        Send event notifications to registered handlers.
        """
        self.globalSiteManager.handle(*objects)

# Make sure there is only one!
Application = _Application()


# vim:sw=4:et:ai
