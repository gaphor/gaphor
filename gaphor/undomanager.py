# vim:sw=4:et:

import gobject
import diacanvas

def get_undo_manager():
    """Return the default undo manager.
    """
    return _default_undo_manager


class TransactionError(Exception):

    def __init__(self, msg):
        self.args = msg


class Transaction(object):
    """A transaction. Every action that is added between a begin_transaction()
    and a commit_transaction() call is recorded in a transaction, do it can
    be played back when a transaction is undone.
    """

    def __init__(self):
        self._actions = []

    def add(self, action):
        self._actions.append(action)

    def can_undo(self):
        return self._actions and True or False

    def undo(self):
        self._actions.reverse()
        for action in self._actions:
            try:
                #log.debug('Undoing action %s' % action)
                action.undo()
            except Exception, e:
                log.error('Error while undoing action %s' % action, e)

    def redo(self):
        self._actions.reverse()
        for action in self._actions:
            try:
                #log.debug('Redoing action %s' % action)
                action.redo()
            except Exception, e:
                log.error('Error while redoing action %s' % action, e)


class UndoManager(gobject.GObject, diacanvas.UndoManager):
    """Simple transaction manager for Gaphor.
    This transaction manager supports nested transactions.
    """

    def __init__(self):
        self.__gobject_init__()
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

#    def add_undo_action(self, action):
#        try:
#            self._short_circuit = True
#            diacanvas.UndoManager.add_undo_action(self, action)
#            self.on_add_undo_action(action)
#        finally:
#            self._short_circuit = False

    # UndoManager interface:

    def on_begin_transaction(self):
        #log.debug('begin_transaction')
        if self._current_transaction:
            raise TransactionError, 'Already in a transaction'

        self._current_transaction = Transaction()
        self.clear_redo_stack()
        self._transaction_depth += 1

    def on_add_undo_action(self, action):
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

    def on_commit_transaction(self):
        #log.debug('commit_transaction')
        if not self._current_transaction:
            return #raise TransactionError, 'No transaction to commit'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            if self._current_transaction.can_undo():
                self._undo_stack.append(self._current_transaction)
            else:
                log.debug('nothing to commit')

            self._current_transaction = None

    def on_discard_transaction(self):
        if not self._current_transaction:
            raise TransactionError, 'No transaction to discard'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction = None

    def on_undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            log.warning('Trying to undo a transaction, while in a transaction')
            self.commit_transaction()
        transaction = self._undo_stack.pop()
        transaction.undo()
        self._redo_stack.append(transaction)

    def on_redo_transaction(self):
        if not self._redo_stack:
            return

        transaction = self._redo_stack.pop()
        transaction.redo()
        self._undo_stack.append(transaction)

    def on_in_transaction(self):
        return self._current_transaction is not None

    def on_can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def on_can_redo(self):
        return bool(self._redo_stack)

gobject.type_register(UndoManager)
diacanvas.set_undo_manager(UndoManager)

# Register as resource:
import gaphor
_default_undo_manager = gaphor.resource(UndoManager)
del gaphor

