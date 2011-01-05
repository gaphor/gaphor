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

from gaphor.misc.logger import Logger
from gaphor.interfaces import IService, IEventFilter
from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent

logger = Logger()

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
        self._event_filter = None
        self.component_registry = None

    def init(self, services=None, opt_parser=None):
        """
        Initialize the application.
        """
        self.opt_parser = opt_parser
        self.load_services(services)
        self.init_all_services()
        if opt_parser:
            self.options, self.args = self.opt_parser.parse_args()
            
            Logger.log_level = Logger.level_map[self.options.logging]
        
    def load_services(self, services=None):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        if services and 'component_registry' not in services:
            services.append('component_registry')

        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IService' % ep.name
            if not services or ep.name in services:
                logger.debug('found service entry point "%s"' % ep.name)
                srv = cls()
                self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        self.init_service('component_registry')
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
            logger.info('initializing service service.%s' % name)
            srv.init(self)

            # Bootstrap symptoms
            if name == 'component_registry':
                self.component_registry = srv

            self.component_registry.register_utility(srv, IService, name)
            self.handle(ServiceInitializedEvent(name, srv))
            return srv

    distribution = property(lambda s: pkg_resources.get_distribution('gaphor'),
                            doc='Get the PkgResources distribution for Gaphor')

    def get_service(self, name):
        try:
            return self.component_registry.get_service(name)
        except component.ComponentLookupError:
            return self.init_service(name)

    def run(self):
        import gtk
        gtk.main()

    def shutdown(self):
        for name, srv in self.component_registry.get_utilities(IService):
            srv.shutdown()
            self.handle(ServiceShutdownEvent(name, srv))
            self.component_registry.unregister_utility(srv, IService, name)
        self.component_registry = None

    # Wrap zope.component's Components methods

    def register_adapter(self, factory, adapts=None, provides=None, name=''):
        """
        Register an adapter (factory) that adapts objects to a specific
        interface. A name can be used to distinguish between different adapters
        that adapt to the same interfaces.
        """
        self.component_registry.register_adapter(factory, adapts, provides,
                              name)

    def unregister_adapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered adapter.
        """
        self.component_registry.unregister_adapter(factory,
                              required, provided, name)

    def register_subscription_adapter(self, factory, adapts=None, provides=None):
        """
        Register a subscription adapter. See registerAdapter().
        """
        self.component_registry.register_subscription_adapter(factory, adapts,
                              provides)

    def unregister_subscription_adapter(self, factory=None,
                          required=None, provided=None, name=u''):
        """
        Unregister a previously registered subscription adapter.
        """
        self.component_registry.unregister_subscription_adapter(factory,
                              required, provided, name)

    def register_handler(self, factory, adapts=None):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emitted through the handle() method.
        """
        self.component_registry.register_handler(factory, adapts)

    def unregister_handler(self, factory=None, required=None):
        """
        Unregister a previously registered handler.
        """
        self.component_registry.unregister_handler(factory, required)
 
    def handle(self, *events):
        """
        Send event notifications to registered handlers.
        """
        self.component_registry.handle(*events)


# Make sure there is only one!
Application = _Application()

# vim:sw=4:et:ai
