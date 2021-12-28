"""Application lifecycle events are managed here."""

from typing import Optional

from gaphor.abc import Service


class ServiceEvent:
    """An event emitted by a service."""

    def __init__(self, service: Service):
        self.service = service


class ServiceInitializedEvent(ServiceEvent):
    """This event is emitted every time a new service has been initialized."""

    def __init__(self, name: str, service: Service):
        super().__init__(service)
        self.name = name


class ServiceShutdownEvent(ServiceEvent):
    """This event is emitted every time a service has been shut down."""

    def __init__(self, name: str, service: Service):
        super().__init__(service)
        self.name = name


class ApplicationShutdown(ServiceEvent):
    """This event is emitted from the application when it has been shut
    down."""


class SessionCreated(ServiceEvent):
    """The session is emitting this event when it's ready to shut down."""

    def __init__(
        self,
        applicaton: Service,
        session: Service,
        filename: Optional[str],
        template: Optional[str],
    ):
        super().__init__(applicaton)
        self.application = applicaton
        self.session = session
        self.filename = filename
        self.template = template


class ActiveSessionChanged(ServiceEvent):
    """Event emitted when a session becomes the active session."""


class SessionShutdownRequested(ServiceEvent):
    """When the application is asked to terminate, it will inform all sessions.

    The user can then save his/her work.
    """


class SessionShutdown(ServiceEvent):
    """The session is emitting this event when it's ready to shut down."""


class ModelLoaded:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename


class ModelSaved:
    def __init__(self, service, filename=None):
        self.service = service
        self.filename = filename


class TransactionBegin:
    """This event denotes the beginning of a transaction.

    Nested (sub-) transactions should not emit this signal.
    """


class TransactionCommit:
    """This event is emitted when a transaction (toplevel) is successfully
    committed."""


class TransactionRollback:
    """If a set of operations fail (e.i.

    due to an exception) the transaction should be marked for rollback.
    This event is emitted to tell the operation has failed.
    """


class ActionEnabled:
    """Signal if an action can be activated or not."""

    def __init__(self, action_name: str, enabled: bool) -> None:
        self.scope, self.name = (
            action_name.split(".", 2) if "." in action_name else ("win", action_name)
        )
        self.enabled = bool(enabled)


class Notification:
    """Inform the user about important events."""

    def __init__(self, message):
        self.message = message
