"""
Application wide events are managed here.
"""

from gaphor.abc import Service


class ServiceEvent:
    """
    An event emitted by a service.
    """

    def __init__(self, service: Service):
        self.service = service


class ServiceInitializedEvent(ServiceEvent):
    """
    This event is emitted every time a new service has been initialized.
    """

    def __init__(self, name: str, service: Service):
        self.name = name
        self.service = service


class ServiceShutdownEvent(ServiceEvent):
    """
    This event is emitted every time a service has been shut down.
    """

    def __init__(self, name: str, service: Service):
        self.name = name
        self.service = service


class TransactionBegin:
    """
    This event denotes the beginning of a transaction.
    Nested (sub-) transactions should not emit this signal.
    """

    pass


class TransactionCommit:
    """
    This event is emitted when a transaction (toplevel) is successfully
    committed.
    """

    pass


class TransactionRollback:
    """
    If a set of operations fail (e.i. due to an exception) the transaction
    should be marked for rollback. This event is emitted to tell the operation
    has failed.
    """

    pass


class ActionEnabled:
    """
    Signal if an action can be activated or not.
    """

    def __init__(self, action_name, enabled: bool):
        self.scope, self.name = (
            action_name.split(".", 2) if "." in action_name else ("win", action_name)
        )
        self.enabled = bool(enabled)
