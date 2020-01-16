"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

from __future__ import annotations

import inspect
import logging
from typing import Dict, Optional, Set, Type

import importlib_metadata

from gaphor.abc import Service
from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent

logger = logging.getLogger(__name__)


class NotInitializedError(Exception):
    pass


class ComponentLookupError(LookupError):
    pass


class _Application:
    """
    The Gaphor application is started from the gaphor.ui module.
    
    This application instance is used to maintain application wide references
    to services and sessions (opened models). It behaves like a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered in the "component_registry" service.
    """

    def __init__(self):
        self.active_session: Optional[Session] = None
        self.sessions: Set[Session] = set()

    def init(self):
        uninitialized_services = load_services("gaphor.appservices")
        self._services_by_name = init_services(uninitialized_services)

    def new_session(self, services=None):
        """
        Initialize an application session.
        """
        session = Session()
        self.sessions.add(session)
        self.active_session = session
        return session

    def has_sessions(self):
        return bool(self.active_session)

    distribution = property(
        lambda s: importlib_metadata.distribution("gaphor"),
        doc="The PkgResources distribution for Gaphor",
    )

    def get_service(self, name):
        if not self.active_session:
            raise NotInitializedError("First call Application.init() to load services")

        return self.active_session.get_service(name)

    def shutdown(self):
        for session in self.sessions:
            self.active_session = None
            # TODO: gently quit via file manager
            session.shutdown()
        self.sessions.clear()

    # def all(self, base: Type[T]) -> Iterator[Tuple[T, str]]:
    def all(self, base):
        return (
            (n, c) for n, c in self._services_by_name.items() if isinstance(c, base)
        )


class Session:
    """
    A user context is a set of services (including UI services)
    that define a window with loaded model.
    """

    def __init__(self, services=None):
        """
        Initialize the application.
        """
        uninitialized_services = load_services("gaphor.services", services)
        services_by_name = init_services(uninitialized_services)

        self.event_manager = services_by_name["event_manager"]
        self.component_registry = services_by_name["component_registry"]

        for name, srv in services_by_name.items():
            logger.info(f"Initializing service {name}")
            self.component_registry.register(name, srv)
            self.event_manager.handle(ServiceInitializedEvent(name, srv))

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("First call Application.init() to load services")

        return self.component_registry.get_service(name)

    def shutdown(self):
        if self.component_registry:
            for name, _srv in self.component_registry.all(Service):
                self.shutdown_service(name)

        self.component_registry = None
        self.event_manager = None

    def shutdown_service(self, name):
        logger.info(f"Shutting down service {name}")
        assert self.component_registry
        assert self.event_manager

        srv = self.component_registry.get_service(name)
        self.event_manager.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister(srv)
        srv.shutdown()


def load_services(scope, services=None) -> Dict[str, Type[Service]]:
    """
    Load services from resources.

    Service should provide an interface `gaphor.abc.Service`.
    """
    uninitialized_services = {}
    for ep in importlib_metadata.entry_points()[scope]:
        cls = ep.load()
        if isinstance(cls, Service):
            raise NameError(f"Entry point {ep.name} doesnt provide Service")
        if not services or ep.name in services:
            logger.debug(f'found service entry point "{ep.name}"')
            uninitialized_services[ep.name] = cls
    return uninitialized_services


def init_services(uninitialized_services):
    """
    Instantiate service definitions, taking into account dependencies
    defined in the constructor.

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


# Make sure there is only one!
Application = _Application()
