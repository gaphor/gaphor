"""
Application wide events are managed here.
"""

from builtins import object
from zope.interface import implementer
from gaphor.interfaces import *


@implementer(IServiceEvent)
class ServiceInitializedEvent(object):
    """
    This event is emitted every time a new service has been initialized.
    """

    def __init__(self, name, service):
        self.name = name
        self.service = service


@implementer(IServiceEvent)
class ServiceShutdownEvent(object):
    """
    This event is emitted every time a service has been shut down.
    """

    def __init__(self, name, service):
        self.name = name
        self.service = service


@implementer(ITransactionEvent)
class TransactionBegin(object):
    """
    This event denotes the beginning of a transaction.
    Nested (sub-) transactions should not emit this signal.
    """

    pass


@implementer(ITransactionEvent)
class TransactionCommit(object):
    """
    This event is emitted when a transaction (toplevel) is successfully
    commited.
    """

    pass


@implementer(ITransactionEvent)
class TransactionRollback(object):
    """
    If a set of operations fail (e.i. due to an exception) the transaction
    should be marked for rollback. This event is emitted to tell the operation
    has failed.
    """

    pass


@implementer(IActionExecutedEvent)
class ActionExecuted(object):
    """
    Once an operation has succesfully been executed this event is raised.
    """

    def __init__(self, name, action):
        self.name = name
        self.action = action


# vim:sw=4:et:ai
