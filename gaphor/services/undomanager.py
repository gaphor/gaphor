# vim:sw=4:et:
"""
Undo management for Gaphor.

Undoing and redoing actions is managed through the UndoManager.

An undo action should be a callable object (called with no arguments).

An undo action should return a callable object that acts as redo function.
If None is returned the undo action is considered to be the redo action as well.

NOTE: it would be nice to use actions in conjunction with functools.partial,
      but that's Python2.5 stuff..
      A replacement is available in gaphor.misc.partial.
"""

from zope import interface
from zope import component
from gaphor.interfaces import IService, IServiceEvent, IActionProvider
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor.transaction import TransactionError, transactional

from gaphor.UML.event import ElementCreateEvent, ElementDeleteEvent, \
                             FlushFactoryEvent, ModelFactoryEvent, \
                             AttributeChangeEvent, AssociationSetEvent, \
                             AssociationAddEvent, AssociationDeleteEvent
from gaphor.UML.interfaces import IElementCreateEvent, IElementDeleteEvent, \
                                  IAttributeChangeEvent, IAssociationChangeEvent

from gaphor.action import action, build_action_group
from gaphor.event import ActionExecuted


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

    @transactional
    def execute(self):
        self._actions.reverse()
        for action in self._actions:
            try:
                action()
            except Exception, e:
                log.error('Error while undoing action %s' % action, e)


class UndoManagerStateChanged(object):
    """
    Event class used to send state changes on the ndo Manager.
    """
    interface.implements(IServiceEvent)

    def __init__(self, service):
        self.service = service


class UndoManager(object):
    """
    Simple transaction manager for Gaphor.
    This transaction manager supports nested transactions.
    
    The Undo manager sports an undo and a redo stack. Each stack contains
    a set of actions that can be executed, just by calling them (e.i action())
    If something is returned by an action, that is considered the callable
    to be used to undo or redo the last performed action.
    """

    interface.implements(IService, IActionProvider)

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="edit">
            <placeholder name="primary">
              <menuitem action="edit-undo" />
              <menuitem action="edit-redo" />
              <separator />
            </placeholder>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []
        self._stack_depth = 20
        self._current_transaction = None
        self._transaction_depth = 0

    def init(self, app):
        self._app = app
        component.provideHandler(self.begin_transaction)
        component.provideHandler(self.commit_transaction)
        component.provideHandler(self.rollback_transaction)
        component.provideHandler(self._action_executed)
        self._provide_undo_handlers()
        self.action_group = build_action_group(self)
        self._action_executed(None)

    def shutdown(self):
        pass

    def clear_undo_stack(self):
        self._undo_stack = []
        self._current_transaction = None

    def clear_redo_stack(self):
        del self._redo_stack[:]

    @component.adapter(TransactionBegin)
    def begin_transaction(self, event=None):
        """
        Add an action to the current transaction
        """
        if self._current_transaction:
            self._transaction_depth += 1
            #raise TransactionError, 'Already in a transaction'
            return

        self._current_transaction = Transaction()
        self._transaction_depth += 1

    def add_undo_action(self, action):
        """
        Add an action to undo. An action
        """
        #log.debug('add_undo_action: %s %s' % (self._current_transaction, action))
        if not self._current_transaction:
            return

        self._current_transaction.add(action)
        component.handle(UndoManagerStateChanged(self))

    @component.adapter(TransactionCommit)
    def commit_transaction(self, event=None):
        #log.debug('commit_transaction')
        if not self._current_transaction:
            return #raise TransactionError, 'No transaction to commit'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            if self._current_transaction.can_execute():
                self.clear_redo_stack()
                self._undo_stack.append(self._current_transaction)
            else:
                pass #log.debug('nothing to commit')

            self._current_transaction = None
        component.handle(UndoManagerStateChanged(self))

    @component.adapter(TransactionRollback)
    def rollback_transaction(self, event=None):
        """
        Roll back the transaction we're in.
        """
        if not self._current_transaction:
            raise TransactionError, 'No transaction to rollback'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction.execute()
            self._current_transaction = None
        # else: mark for rollback?
        component.handle(UndoManagerStateChanged(self))

    def discard_transaction(self):

        if not self._current_transaction:
            raise TransactionError, 'No transaction to discard'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction = None
        component.handle(UndoManagerStateChanged(self))

    @action(name='edit-undo', stock_id='gtk-undo')
    def undo_transaction(self):
        if not self._undo_stack:
            return

        if self._current_transaction:
            log.warning('Trying to undo a transaction, while in a transaction')
            self.commit_transaction()
        transaction = self._undo_stack.pop()

        self._current_transaction = Transaction()
        self._transaction_depth += 1

        transaction.execute()

        assert self._transaction_depth == 1
        self._redo_stack.append(self._current_transaction)
        self._current_transaction = None
        self._transaction_depth = 0
        component.handle(UndoManagerStateChanged(self))

    @action(name='edit-redo', stock_id='gtk-redo')
    def redo_transaction(self):
        if not self._redo_stack:
            return

        transaction = self._redo_stack.pop()

        self._current_transaction = Transaction()
        self._transaction_depth += 1

        transaction.execute()

        assert self._transaction_depth == 1
        self._undo_stack.append(self._current_transaction)
        self._current_transaction = None
        self._transaction_depth = 0

        component.handle(UndoManagerStateChanged(self))

    def in_transaction(self):
        return self._current_transaction is not None

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)


    @component.adapter(ActionExecuted)
    def _action_executed(self, event):
        self.action_group.get_action('edit-undo').set_sensitive(self.can_undo())
        self.action_group.get_action('edit-redo').set_sensitive(self.can_redo())

    ##
    ## Undo Handlers
    ##

    def _provide_undo_handlers(self):
        component.provideHandler(self.undo_create_event)
        component.provideHandler(self.undo_delete_event)
        component.provideHandler(self.undo_attribute_change_event)
        component.provideHandler(self.undo_association_set_event)
        component.provideHandler(self.undo_association_add_event)
        component.provideHandler(self.undo_association_delete_event)

        #
        # Direct revert-statements from gaphas to the undomanager
        from gaphas import state
        state.observers.add(state.revert_handler)

        def _undo_handler(event):
            self.add_undo_action(lambda: state.saveapply(*event));

        state.subscribers.add(_undo_handler)


    @component.adapter(IElementCreateEvent)
    def undo_create_event(self, event):
        factory = event.service
        element = event.element
        def _undo_create_event():
            try:
                del factory._elements[element.id]
            except KeyError:
                pass # Key was probably already removed in an unlink call
            factory.notify(element, 'remove')
            component.handle(ElementDeleteEvent(factory, element))
        self.add_undo_action(_undo_create_event)


    @component.adapter(IElementDeleteEvent)
    def undo_delete_event(self, event):
        factory = event.service
        element = event.element
        def _undo_delete_event():
            factory._elements[element.id] = element
            factory.notify(element, 'create')
            component.handle(ElementCreateEvent(factory, element))
        self.add_undo_action(_undo_delete_event)


    @component.adapter(IAttributeChangeEvent)
    def undo_attribute_change_event(self, event):
        attribute = event.property
        obj = event.element
        value = event.old_value
        def _undo_attribute_change_event():
            attribute._set(obj, value)
        self.add_undo_action(_undo_attribute_change_event)


    @component.adapter(AssociationSetEvent)
    def undo_association_set_event(self, event):
        association = event.property
        obj = event.element
        value = event.old_value
        def _undo_association_set_event():
            #print 'undoing action', obj, value
            # Tell the assoctaion it should not need to let the opposite
            # side connect (it has it's own signal)
            association._set(obj, value, from_opposite=True)
        self.add_undo_action(_undo_association_set_event)


    @component.adapter(AssociationAddEvent)
    def undo_association_add_event(self, event):
        association = event.property
        obj = event.element
        value = event.new_value
        def _undo_association_add_event():
            #print 'undoing action', obj, value
            # Tell the assoctaion it should not need to let the opposite
            # side connect (it has it's own signal)
            association._del(obj, value, from_opposite=True)
        self.add_undo_action(_undo_association_add_event)


    @component.adapter(AssociationDeleteEvent)
    def undo_association_delete_event(self, event):
        association = event.property
        obj = event.element
        value = event.old_value
        def _undo_association_delete_event():
            #print 'undoing action', obj, value
            # Tell the assoctaion it should not need to let the opposite
            # side connect (it has it's own signal)
            association._set(obj, value, from_opposite=True)
        self.add_undo_action(_undo_association_delete_event)


# vim:sw=4:et:ai
