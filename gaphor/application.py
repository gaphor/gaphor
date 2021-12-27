"""The Application object. One application should be available.

An application can host multiple sessions. From a user point of view a
session is represented as a window in which a diagram can be edited.
"""

from __future__ import annotations

import importlib.metadata
import logging
from typing import Iterator, TypeVar, cast

from gaphor import transaction
from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.core.eventmanager import EventManager
from gaphor.entrypoint import initialize
from gaphor.event import (
    ActiveSessionChanged,
    ApplicationShutdown,
    ModelLoaded,
    ModelSaved,
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
    """The distribution metadata for Gaphor."""
    return importlib.metadata.distribution("gaphor")


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
        self._active_session: Session | None = None
        self._sessions: set[Session] = set()

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
    def sessions(self):
        return self._sessions

    @property
    def active_session(self):
        return self._active_session

    def new_session(self, *, filename=None, template=None, services=None, force=False):
        if filename is None and template is None:
            return self._new_session(services=services)

        if filename and not force:
            for session in self._sessions:
                if session.filename == filename:
                    session.foreground()
                    return

        return self._new_session(
            filename=filename, template=template, services=services
        )

    def _new_session(self, filename=None, template=None, services=None):
        """Initialize an application session."""
        session = Session(services=services)

        @event_handler(ActiveSessionChanged)
        def on_active_session_changed(event):
            self._active_session = session

        @event_handler(SessionShutdown)
        def on_session_shutdown(event):
            self.shutdown_session(session)
            if not self._sessions:
                self.quit()

        event_manager = session.get_service("event_manager")
        event_manager.subscribe(on_active_session_changed)
        event_manager.subscribe(on_session_shutdown)

        self._sessions.add(session)

        session_created = SessionCreated(self, session, filename, template)
        event_manager.handle(session_created)
        self.event_manager.handle(session_created)
        session.foreground()

        return session

    def has_sessions(self):
        return bool(self._active_session)

    def has_session(self, filename):
        return any(
            session for session in self._sessions if session.filename == filename
        )

    def shutdown_session(self, session):
        assert session
        session.shutdown()
        self._sessions.discard(session)
        if session is self._active_session:
            self._active_session = None

    def shutdown(self):
        """Forcibly shut down all sessions. No questions asked.

        This is mainly for testing purposes.
        """
        transaction.subscribers.discard(self._transaction_proxy)

        while self._sessions:
            self.shutdown_session(self._sessions.pop())

        self.event_manager.handle(ApplicationShutdown(self))

        for c in self._services_by_name.values():
            if c is not self:
                c.shutdown()
        self._services_by_name.clear()

    @action(name="app.quit", shortcut="<Primary>q")
    def quit(self):
        """The user's application Quit command."""
        for session in list(self._sessions):
            self._active_session = session
            event_manager = session.get_service("event_manager")
            event_manager.handle(SessionShutdownRequested(self))
            if self._active_session == session:
                logger.info("Window not closed, abort quit operation")
                return False
        self.shutdown()
        return True

    def all(self, base: type[T]) -> Iterator[tuple[str, T]]:
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
        services_by_name: dict[str, Service] = initialize("gaphor.services", services)
        self._filename = None

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

        self.event_manager.subscribe(self.on_filename_changed)

    def get_service(self, name):
        if not self.component_registry:
            raise NotInitializedError("Session is no longer alive")

        return self.component_registry.get_service(name)

    @property
    def filename(self):
        return self._filename

    def foreground(self):
        self.event_manager.handle(ActiveSessionChanged(self))

    def shutdown(self):
        if self.component_registry:
            for name, srv in reversed(list(self.component_registry.all(Service))):  # type: ignore[misc]
                self.shutdown_service(name, srv)

    def shutdown_service(self, name, srv):
        logger.info(f"Shutting down service {name}")

        self.event_manager.handle(ServiceShutdownEvent(name, srv))
        self.component_registry.unregister(srv)
        srv.shutdown()

    @event_handler(SessionCreated, ModelLoaded, ModelSaved)
    def on_filename_changed(self, event):
        self._filename = event.filename
