"""
Application wide events are managed here.
"""

from zope import interface
from gaphor.interfaces import *

class TransactionBegin(object):
    """
    This event denotes the beginning of an transaction.
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


# vim:sw=4:et:ai

