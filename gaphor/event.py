"""
Application wide events are managed here.
"""

from __future__ import absolute_import

from gaphor.interfaces import *


class ServiceInitializedEvent(object):
    """
    This event is emitted every time a new service has been initialized.
    """
    interface.implements(IServiceEvent)

    def __init__(self, name, service):
        self.name = name
        self.service = service


class ServiceShutdownEvent(object):
    """
    This event is emitted every time a service has been shut down.
    """
    interface.implements(IServiceEvent)

    def __init__(self, name, service):
        self.name = name
        self.service = service


class TransactionBegin(object):
    """
    This event denotes the beginning of a transaction.
    Nested (sub-) transactions should not emit this signal.
    """
    interface.implements(ITransactionEvent)


class TransactionCommit(object):
    """
    This event is emitted when a transaction (toplevel) is successfully
    commited.
    """
    interface.implements(ITransactionEvent)


class TransactionRollback(object):
    """
    If a set of operations fail (e.i. due to an exception) the transaction
    should be marked for rollback. This event is emitted to tell the operation
    has failed.
    """
    interface.implements(ITransactionEvent)


class ActionExecuted(object):
    """
    Once an operation has succesfully been executed this event is raised.
    """
    interface.implements(IActionExecutedEvent)

    def __init__(self, name, action):
        self.name = name
        self.action = action

# vim:sw=4:et:ai
