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
    _ESSENTIAL_SERVICES = ['component_registry']
    
    def __init__(self):
        self._uninitialized_services = {}
        self._event_filter = None


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
        

    essential_services = property(lambda s: s._ESSENTIAL_SERVICES, doc= """
        Provide an ordered list of services that need to be loaded first.
        """)

    def load_services(self, services=None):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        # Ensure essential services are always loaded.
        if services:
            for name in self.essential_services:
               if name not in services:
                    services.append(name)

        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IService' % ep.name
            if not services or ep.name in services:
                logger.debug('found service entry point "%s"' % ep.name)
                srv = cls()
                self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        for name in self.essential_services:
            self.init_service(name)
        while self._uninitialized_services:
            self.init_service(self._uninitialized_services.iterkeys().next())

    def init_service(self, name):
        """
        Initialize a not yet initialized service.

        Raises ComponentLookupError if the service has not been found
        """
        try:
            srv = self._uninitialized_services.pop(name)
        except KeyError:
            raise component.ComponentLookupError(IService, name)
        else:
            logger.info('initializing service service.%s' % name)
            srv.init(self)

            # Bootstrap symptoms
            if name in self.essential_services:
                setattr(self, name, srv)

            self.component_registry.register_utility(srv, IService, name)
            self.component_registry.handle(ServiceInitializedEvent(name, srv))
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
            if name not in self.essential_services:
                self.shutdown_service(name)

        for name in reversed(self.essential_services):
            self.shutdown_service(name)
            setattr(self, name, None)


    def shutdown_service(self, name):
        srv = self.component_registry.get_service(name)
        self.component_registry.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister_utility(srv, IService, name)
        srv.shutdown()


# Make sure there is only one!
Application = _Application()

# vim:sw=4:et:ai
