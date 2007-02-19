# vim:sw=4:et:
"""
Undo management for Gaphor.

Undoing and redoing actions is managed through the UndoManager.

An undo action should be a callable object (called with no arguments).

An undo action should return a callable object that acts as redo function.
If None is returned the undo action is considered to be the redo action as well.

NOTE: it would be nice to use actions in conjunction with functools.partial,
      but that's Python2.5 stuff..
"""


def get_undo_manager():
    """Return the default undo manager.
    """
    return _default_undo_manager


def transactional(func):
    """
    Descriptor. Begins a transaction around the method/function.

    TODO: In casse of an exception, roll back the transaction if the transaction
    level == 1.
    """
    def wrapper(*args, **kwargs):
        undo_manager = get_undo_manager()
        undo_manager.begin_transaction()
        try:
            func(*args, **kwargs)
        finally:
            undo_manager.commit_transaction()
    return wrapper


class TransactionError(Exception):

    def __init__(self, msg):
        self.args = msg


class Transaction(object):
    """
    A transaction. Every action that is added between a begin_transaction()
    and a commit_transaction() call is recorded in a transaction, so it can
    be played back when a transaction is executed. This executing a
    transaction has the effect of performing the actions recorded, which will
    typically undo actions performed by the user.
    """

    def __init__(self):
        self._actions = []

    def add(self, action):
        self._actions.append(action)

    def can_execute(self):
        return self._actions and True or False

    def execute(self):
        self._actions.reverse()
        contra_transaction = Transaction()
        for action in self._actions:
            try:
                contra_action = action()
                contra_transaction.add(contra_action or action)
            except Exception, e:
                log.error('Error while undoing action %s' % action, e)
        return contra_transaction

class UndoManager(object):
    """
    Simple transaction manager for Gaphor.
    This transaction manager supports nested transactions.
    
    The Undo manager sports an undo and a redo stack. Each stack contains
    a set of actions that can be executed, just by calling them (e.i action())
    If something is returned by an action, that is considered the callable
    to be used to undo or redo the last performed action.
    """

    def __init__(self):
        self._in_undo = False
        self._undo_stack = []
        self._redo_stack = []
        self._stack_depth = 20
        self._current_transaction = None
        self._transaction_depth = 0
        self._short_circuit = False

    def clear_undo_stack(self):
        self._undo_stack = []
        self._current_transaction = None

    def clear_redo_stack(self):
        self._redo_stack = []

    def begin_transaction(self):
        """Add an action to the current transaction
        """
        if self._in_undo:
            return

        #log.debug('begin_transaction')
        if self._current_transaction:
            self._transaction_depth += 1
            #raise TransactionError, 'Already in a transaction'
            return

        self._current_transaction = Transaction()
        self.clear_redo_stack()
        self._transaction_depth += 1

    def add_undo_action(self, action):
        """Add an action to undo. An action
        """
        if self._short_circuit:
            return

        #log.debug('add_undo_action: %s %s' % (self._current_transaction, action))
        if not self._current_transaction:
            return

        if self._redo_stack:
            self.clear_redo_stack()

        self._current_transaction.add(action)

    def commit_transaction(self):
        if self._in_undo:
            return

        #log.debug('commit_transaction')
        if not self._current_transaction:
            return #raise TransactionError, 'No transaction to commit'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            if self._current_transaction.can_execute():
                self._undo_stack.append(self._current_transaction)
            else:
                pass #log.debug('nothing to commit')

            self._current_transaction = None

    def discard_transaction(self):
        if self._in_undo:
            return

        if not self._current_transaction:
            raise TransactionError, 'No transaction to discard'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction = None

    def undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            log.warning('Trying to undo a transaction, while in a transaction')
            self.commit_transaction()
        transaction = self._undo_stack.pop()
        try:
            self._in_undo = True
            redo_transaction = transaction.execute()
        finally:
            self._in_undo = False
        self._redo_stack.append(redo_transaction)

    def redo_transaction(self):
        if not self._redo_stack:
            return

        transaction = self._redo_stack.pop()
        try:
            self._in_undo = True
            undo_transaction = transaction.execute()
        finally:
            self._in_undo = False
        self._undo_stack.append(undo_transaction)

    def in_transaction(self):
        return self._current_transaction is not None

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)


# Register as resource:
import gaphor
_default_undo_manager = gaphor.resource(UndoManager)
del gaphor

