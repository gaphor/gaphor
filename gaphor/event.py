"""
Application wide events are managed here.
"""

from gaphor.interfaces import *


class ServiceEvent:
    """
    An event emitted by a service.
    """

    def __init__(self, service):
        self.service = service


class ServiceInitializedEvent(ServiceEvent):
    """
    This event is emitted every time a new service has been initialized.
    """

    def __init__(self, name, service):
        self.name = name
        self.service = service


class ServiceShutdownEvent(ServiceEvent):
    """
    This event is emitted every time a service has been shut down.
    """

    def __init__(self, name, service):
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


class ActionExecuted:
    """
    Once an operation has successfully been executed this event is raised.
    """

    def __init__(self, name, action):
        self.name = name
        self.action = action
