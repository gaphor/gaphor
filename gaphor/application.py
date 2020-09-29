"""The Application object. One application should be available.

An application can host multiple sessions. From a user point of view a
session is represented as a window in which a diagram can be edited.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterator, Optional, Set, Tuple, Type, TypeVar, cast

import importlib_metadata

from gaphor import transaction
from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.core.eventmanager import EventManager
from gaphor.entrypoint import initialize
from gaphor.event import (
    ActiveSessionChanged,
    ApplicationShutdown,
    ServiceInitializedEvent,
    ServiceShutdownEvent,
    SessionCreated,
    SessionShutdown,
    SessionShutdownRequested,
)
from gaphor.services.componentregistry import ComponentRegistry

T = TypeVar("T")


logger = logging.getLogger(__name__)


def distribution():
    """The PkgResources distribution for Gaphor."""
    return importlib_metadata.distribution("gaphor")


class NotInitializedError(Exception):
    pass


class Application(Service, ActionProvider):
    """The Gaphor application is started from the gaphor.ui module.

    This application instance is used to maintain application wide references
    to services and sessions (opened models). It behaves like a singleton in many ways.

    The Application is responsible for loading services and plugins. Services
    are registered in the "component_registry" service.
    """

    def __init__(self):
        self._active_session: Optional[Session] = None
        self.sessions: Set[Session] = set()

        self._services_by_name = initialize("gaphor.appservices", application=self)

        self.event_manager: EventManager = cast(
            EventManager, self._services_by_name["event_manager"]
        )

        transaction.subscribers.add(self._transaction_proxy)

    def get_service(self, name):
        if not self._services_by_name:
            raise NotInitializedError("Session is no longer alive")

        return self._services_by_name[name]

    @property
    def active_session(self):
        return self._active_session

    def new_session(self, services=None):
        """Initialize an application session."""
        session = Session()

        @event_handler(ActiveSessionChanged)
        def on_active_session_changed(event):
            self._active_session = session

        @event_handler(SessionShutdown)
        def on_session_shutdown(event):
            self.shutdown_session(session)
            if not self.sessions:
                self.quit()

        event_manager = session.get_service("event_manager")
        event_manager.subscribe(on_active_session_changed)
        event_manager.subscribe(on_session_shutdown)

        self.sessions.add(session)
        self._active_session = session

        self.event_manager.handle(SessionCreated(self, session))
        return session

    def has_sessions(self):
        return bool(self._active_session)

    def shutdown_session(self, session):
        assert session
        session.shutdown()
        self.sessions.discard(session)
        if session is self._active_session:
            self._active_session = None

    def shutdown(self):
        """Forcibly shut down all sessions. No questions asked.

        This is mainly for testing purposes.
        """
        transaction.subscribers.discard(self._transaction_proxy)

        while self.sessions:
            self.shutdown_session(self.sessions.pop())

        self.event_manager.handle(ApplicationShutdown(self))

        for c in self._services_by_name.values():
            if c is not self:
                c.shutdown()
        self._services_by_name.clear()

    @action(name="app.quit", shortcut="<Primary>q")
    def quit(self):
        """The user's application Quit command."""
        for session in list(self.sessions):
            self._active_session = session
            event_manager = session.get_service("event_manager")
            event_manager.handle(SessionShutdownRequested(self))
            if self._active_session == session:
                logger.info("Window not closed, abort quit operation")
                return False
        self.shutdown()
        return True

    def all(self, base: Type[T]) -> Iterator[Tuple[str, T]]:
        return (
            (n, c) for n, c in self._services_by_name.items() if isinstance(c, base)
        )

    def _transaction_proxy(self, event):
        if self._active_session:
            self._active_session.event_manager.handle(event)


class Session(Service):
    """A user context is a set of services (including UI services) that define
    a window with loaded model."""

    def __init__(self, services=None):
        """Initialize the application."""
        services_by_name: Dict[str, Service] = initialize("gaphor.services", services)

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
