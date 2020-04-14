"""
The Application object. One application should be available.

An application can host multiple sessions. From a user point of
view a session is represented as a window in which a diagram
can be edited.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterator, Optional, Set, Tuple, Type, TypeVar, cast

import importlib_metadata

from gaphor import transaction
from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core.eventmanager import EventManager
from gaphor.entrypoint import init_entrypoints, load_entrypoints
from gaphor.event import (
    ServiceInitializedEvent,
    ServiceShutdownEvent,
    SessionShutdownRequested,
)
from gaphor.services.componentregistry import ComponentRegistry

T = TypeVar("T")


logger = logging.getLogger(__name__)


def distribution():
    """
    The PkgResources distribution for Gaphor
    """
    return importlib_metadata.distribution("gaphor")


class NotInitializedError(Exception):
    pass


class Application(Service, ActionProvider):
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

        uninitialized_services: Dict[str, Type[Service]] = load_entrypoints(
            "gaphor.appservices"
        )
        self._services_by_name = init_entrypoints(
            uninitialized_services, application=self
        )

        transaction.subscribers.add(self._transaction_proxy)

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
        transaction.subscribers.discard(self._transaction_proxy)

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
        self.shutdown()

    def all(self, base: Type[T]) -> Iterator[Tuple[str, T]]:
        return (
            (n, c) for n, c in self._services_by_name.items() if isinstance(c, base)
        )

    def _transaction_proxy(self, event):
        if self.active_session:
            self.active_session.event_manager.handle(event)


class Session:
    """
    A user context is a set of services (including UI services)
    that define a window with loaded model.
    """

    def __init__(self, services=None):
        """
        Initialize the application.
        """
        uninitialized_services: Dict[str, Type[Service]] = load_entrypoints(
            "gaphor.services", services
        )
        services_by_name = init_entrypoints(uninitialized_services)

        self.event_manager: EventManager = cast(
            EventManager, services_by_name["event_manager"]
        )
        self.component_registry: ComponentRegistry = cast(
            ComponentRegistry, services_by_name["component_registry"]
        )

        for name, srv in services_by_name.items():
            logger.info(f"Initializing service {name}")
            self.component_registry.register(name, srv)
            self.event_manager.handle(ServiceInitializedEvent(name, srv))

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("Session is no longer alive")

        return self.component_registry.get_service(name)

    def shutdown(self):
        if self.component_registry:
            for name, srv in self.component_registry.all(Service):  # type: ignore[misc]
                self.shutdown_service(name, srv)

    def shutdown_service(self, name, srv):
        logger.info(f"Shutting down service {name}")

        self.event_manager.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister(srv)
        srv.shutdown()
