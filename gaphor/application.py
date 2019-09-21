"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

from typing import Dict, Type
import logging
import inspect
import importlib_metadata

from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent
from gaphor.abc import Service

logger = logging.getLogger(__name__)


class NotInitializedError(Exception):
    pass


class ComponentLookupError(LookupError):
    pass


class _Application:
    """
    The Gaphor application is started from the Application instance. It behaves
    like a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered in the "component_registry" service.
    """

    def __init__(self):
        self._uninitialized_services: Dict[str, Type[Service]] = {}
        self._app = None
        self.component_registry = None
        self.event_manager = None

    def init(self, services=None):
        """
        Initialize the application.
        """
        self.load_services(services)
        self.init_all_services()

    def load_services(self, services=None):
        """
        Load services from resources.

        Service should provide an interface gaphor.abc.Service.
        """
        for ep in importlib_metadata.entry_points()["gaphor.services"]:
            cls = ep.load()
            if isinstance(cls, Service):
                raise NameError(f"Entry point {ep.name} doesnt provide Service")
            if not services or ep.name in services:
                logger.debug(f'found service entry point "{ep.name}"')
                self._uninitialized_services[ep.name] = cls

    def init_all_services(self):
        services_by_name = init_services(self._uninitialized_services)

        self.event_manager = services_by_name["event_manager"]
        self.component_registry = services_by_name["component_registry"]

        for name, srv in services_by_name.items():
            logger.info(f"Initializing service {name}")
            self.component_registry.register(srv, name)
            self.event_manager.handle(ServiceInitializedEvent(name, srv))

    distribution = property(
        lambda s: importlib_metadata.distribution("gaphor"),
        doc="The PkgResources distribution for Gaphor",
    )

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("First call Application.init() to load services")

        return self.component_registry.get_service(name)

    def shutdown(self):
        for srv, name in self.component_registry.all(Service):
            self.shutdown_service(name)

        self.component_registry = None

    def shutdown_service(self, name):
        logger.info(f"Shutting down service {name}")
        srv = self.component_registry.get_service(name)
        self.event_manager.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister(srv)
        srv.shutdown()

    def run(self, model=None):
        """Start the GUI application.

        The file_manager service is used here to load a Gaphor model if one was
        specified on the command line."""

        from gaphor.ui import run

        run(self, model)


# Make sure there is only one!
Application = _Application()


def init_services(uninitialized_services):
    """
    Given a dictionary `{name: service-class}`,
    return a map `{name: service-instance}`.
    """
    ready: Dict[str, Service] = {}

    def pop(name):
        try:
            return uninitialized_services.pop(name)
        except KeyError:
            return None

    def init(name, cls):
        kwargs = {}
        for dep in inspect.signature(cls).parameters:
            if dep not in ready:
                depcls = pop(dep)
                if depcls:
                    kwargs[dep] = init(dep, depcls)
                else:
                    logger.info(
                        f"Service {name} parameter {dep} does not reference a service"
                    )
            else:
                kwargs[dep] = ready[dep]
        srv = cls(**kwargs)
        ready[name] = srv
        return srv

    while uninitialized_services:
        name = next(iter(uninitialized_services.keys()))
        cls = pop(name)
        init(name, cls)

    return ready
