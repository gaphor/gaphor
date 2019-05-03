"""
Application wide events are managed here.
"""

from gaphor.interfaces import *


class ServiceEvent(object):
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


class TransactionBegin(object):
    """
    This event denotes the beginning of a transaction.
    Nested (sub-) transactions should not emit this signal.
    """

    pass


class TransactionCommit(object):
    """
    This event is emitted when a transaction (toplevel) is successfully
    committed.
    """

    pass


class TransactionRollback(object):
    """
    If a set of operations fail (e.i. due to an exception) the transaction
    should be marked for rollback. This event is emitted to tell the operation
    has failed.
    """

    pass


class ActionExecuted(object):
    """
    Once an operation has successfully been executed this event is raised.
    """

    def __init__(self, name, action):
        self.name = name
        self.action = action
