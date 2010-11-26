"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

import os
import pkg_resources
from zope import component

from gaphor.misc.logger import Logger
from gaphor.interfaces import IService, IEventFilter
from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent
import gaphor.UML

if os.name == 'nt':
    home = 'USERPROFILE'
else:
    home = 'HOME'

user_data_dir = os.path.join(os.getenv(home), '.gaphor')

class _Application(object):
    """
    The Gaphor application is started from the Application instance. It behaves
    like a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered as "utilities" in the application registry.

    Methods are provided that wrap zope.component's handle, adapter and
    subscription registrations. In addition to registration methods also
    unregister methods are provided. This way services can be properly
    unregistered on shutdown for example.
    """

    # interface.implements(IApplication)
    
    def __init__(self):
        self._uninitialized_services = {}
        self.init_components()
        self._event_filter = None

    def init(self, services=None, opt_parser=None):
        """
        Initialize the application.
        """
        self.opt_parser = opt_parser
        self.load_services(services)
        self.init_all_services()
        self.options, self.args = self.opt_parser.parse_args()
        
        log.log_level = Logger.level_map[self.options.logging]
        
    def init_components(self):
        """
        Initialize application level component registry.

        Frequently used query methods are overridden on the zope.component
        module.
        """
        #self._components = component.getGlobalSiteManager()
        #return

        self._components = component.registry.Components(name='app',
                               bases=(component.getGlobalSiteManager(),))

        # Make sure component.handle() and query methods works.
        # TODO: eventually all queries should be done through the Application
        # instance.
        component.handle = self.handle
        component.getMultiAdapter = self._components.getMultiAdapter
        component.queryMultiAdapter = self._components.queryMultiAdapter
        component.getAdapter = self._components.getAdapter
        component.queryAdapter = self._components.queryAdapter
        component.getAdapters = self._components.getAdapters
        component.getUtility = self._components.getUtility
        component.queryUtility = self._components.queryUtility
        component.getUtilitiesFor = self._components.getUtilitiesFor

    def load_services(self, services=None):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        for ep in pkg_resources.iter_entry_points('gaphor.services'):
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
            self._components.registerUtility(srv, IService, name)
            self.handle(ServiceInitializedEvent(name, srv))
            return srv

    distribution = property(lambda s: pkg_resources.get_distribution('gaphor'),
                            doc='Get the PkgResources distribution for Gaphor')

    def get_service(self, name):
        try:
            return self._components.getUtility(IService, name)
        except component.ComponentLookupError:
            return self.init_service(name)

    def run(self):
        import gtk
        gtk.main()

    def shutdown(self):
        for name, srv in self._components.getUtilitiesFor(IService):
            srv.shutdown()
            self.handle(ServiceShutdownEvent(name, srv))
            self._components.unregisterUtility(srv, IService, name)

        # Re-initialize components registry
        self.init_components()

    # Wrap zope.component's Components methods

    def register_adapter(self, factory, adapts=None, provides=None, name=''):
        """
        Register an adapter (factory) that adapts objects to a specific
        interface. A name can be used to distinguish between different adapters
        that adapt to the same interfaces.
        """
        self._components.registerAdapter(factory, adapts, provides,
                              name, event=False)

    def unregister_adapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered adapter.
        """
        self._components.unregisterAdapter(factory,
                              required, provided, name)

    def register_subscription_adapter(self, factory, adapts=None, provides=None):
        """
        Register a subscription adapter. See registerAdapter().
        """
        self._components.registerSubscriptionAdapter(factory, adapts,
                              provides, event=False)

    def unregister_subscription_adapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered subscription adapter.
        """
        self._components.unregisterSubscriptionAdapter(factory,
                              required, provided, name)

    def register_handler(self, factory, adapts=None):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emitted through the handle() method.
        """
        self._components.registerHandler(factory, adapts, event=False)

    def unregister_handler(self, factory=None, required=None):
        """
        Unregister a previously registered handler.
        """
        self._components.unregisterHandler(factory, required)
 
    def _filter(self, objects):
        filtered = list(objects)
        for o in objects:
            for adapter in self._components.subscribers(objects, IEventFilter):
                if adapter.filter():
                    # event is blocked
                    filtered.remove(o)
                    break
        return filtered

    def handle(self, *events):
        """
        Send event notifications to registered handlers.
        """
        objects = self._filter(events)
        if objects:
            self._components.handle(*events)


# Make sure there is only one!
Application = _Application()

# vim:sw=4:et:ai
