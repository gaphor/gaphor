"""
Transation support for Gaphor
"""

import sys
from zope import interface, component
from gaphor.interfaces import ITransaction
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback

def transactional(func):
    def _transactional(*args, **kwargs):
        tx = Transaction()
        try:
	    func(*args, **kwargs)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error('Transaction terminated due to an exception, performing a rollback', exc_value)
            try:
                tx.rollback()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error('Rollback failed', exc_value)
            raise
        else:
            tx.commit()
    return _transactional

class TransactionError(Exception):
    """
    Errors related to the transaction module.
    """


class Transaction(object):
    interface.implements(ITransaction)

    _stack= []

    def __init__(self):
        self._need_rollback = False
        if not self._stack:
            component.handle(TransactionBegin())
        self._stack.append(self)

    def commit(self):
        self._close()
#        if self._need_rollback:
#            log.warning('Tried to commit a transaction already marked for rollback.')
        if not self._stack:
            if self._need_rollback:
                component.handle(TransactionRollback())
            else:
                component.handle(TransactionCommit())

    def rollback(self):
        self._close()
        # Mark every tx on the stack for rollback
        for tx in self._stack:
            tx._need_rollback = True
        if not self._stack:
            component.handle(TransactionRollback())

    def _close(self):
        try:
            last = self._stack.pop()
        except IndexError:
            raise TransactionError, 'No Transaction on stack.'
        if last is not self:
            self._stack.append(last)
            raise TransactionError, 'Transaction on stack is not the transaction being closed.'


# vim: sw=4:et:ai
