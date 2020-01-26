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
from typing import Dict, Iterator, Optional, Set, Tuple, Type, TypeVar

import importlib_metadata

from gaphor import transaction
from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.event import (
    ServiceInitializedEvent,
    ServiceShutdownEvent,
    SessionShutdownRequested,
)

T = TypeVar("T")


logger = logging.getLogger(__name__)


def distribution():
    """
    The PkgResources distribution for Gaphor
    """
    return importlib_metadata.distribution("gaphor")


class NotInitializedError(Exception):
    pass


class ComponentLookupError(LookupError):
    pass


class _Application(Service, ActionProvider):
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
        self._services_by_name: Dict[str, Service] = {}

    def init(self):
        uninitialized_services = load_services("gaphor.appservices")
        self._services_by_name = init_services(uninitialized_services, application=self)

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

    def shutdown_session(self, session):
        assert session
        session.shutdown()
        self.sessions.discard(session)
        if session is self.active_session:
            self.active_session = None

    def shutdown(self):
        """
        Forcibly shut down all sessions. No questions asked.

        This is mainly for testing purposes.
        """
        while self.sessions:
            self.shutdown_session(self.sessions.pop())

        for c in self._services_by_name.values():
            if c is not self:
                c.shutdown()
        self._services_by_name.clear()

    @action(name="app.quit", shortcut="<Primary>q")
    def quit(self):
        """
        The user's application Quit command.
        """
        for session in list(self.sessions):
            self.active_session = session
            event_manager = session.get_service("event_manager")
            event_manager.handle(SessionShutdownRequested(self))
            if self.active_session == session:
                logger.info("Window not closed, abort quit operation")
                return

    def all(self, base: Type[T]) -> Iterator[Tuple[str, T]]:
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

        transaction.subscribers.add(self._transaction_proxy)

    def _transaction_proxy(self, event):
        if self is Application.active_session:
            self.event_manager.handle(event)

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("Session is no longer alive")

        return self.component_registry.get_service(name)

    def shutdown(self):
        transaction.subscribers.discard(self._transaction_proxy)

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


def init_services(uninitialized_services, **known_services):
    """
    Instantiate service definitions, taking into account dependencies
    defined in the constructor.

    Given a dictionary `{name: service-class}`,
    return a map `{name: service-instance}`.
    """
    ready: Dict[str, Service] = dict(known_services)

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
