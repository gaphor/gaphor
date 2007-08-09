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

from gaphas import state
from gaphor.interfaces import IService, IServiceEvent, IActionProvider
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor.transaction import TransactionError, transactional

from gaphor.UML.event import ElementCreateEvent, ElementDeleteEvent, \
                             FlushFactoryEvent, ModelFactoryEvent, \
                             AttributeChangeEvent, AssociationSetEvent, \
                             AssociationAddEvent, AssociationDeleteEvent
from gaphor.UML.interfaces import IElementCreateEvent, IElementDeleteEvent, \
                                  IAttributeChangeEvent, IModelFactoryEvent, \
                                  IAssociationChangeEvent

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
        <toolbar action="mainwindow-toolbar">
          <toolitem action="edit-undo" />
          <toolitem action="edit-redo" />
          <separator />
        </toolbar>
      </ui>
    """

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []
        self._stack_depth = 20
        self._current_transaction = None
        self._transaction_depth = 0
        self.action_group = build_action_group(self)

    def init(self, app):
        self._app = app
        app.register_handler(self.reset)
        app.register_handler(self.begin_transaction)
        app.register_handler(self.commit_transaction)
        app.register_handler(self.rollback_transaction)
        app.register_handler(self._action_executed)
        self._register_undo_handlers()
        self._action_executed()

    def shutdown(self):
        self._app.unregister_handler(self.reset)
        self._app.unregister_handler(self.begin_transaction)
        self._app.unregister_handler(self.commit_transaction)
        self._app.unregister_handler(self.rollback_transaction)
        self._app.unregister_handler(self._action_executed)
        self._unregister_undo_handlers()

    def clear_undo_stack(self):
        self._undo_stack = []
        self._current_transaction = None

    def clear_redo_stack(self):
        del self._redo_stack[:]
    
    @component.adapter(IModelFactoryEvent)
    def reset(self, event=None):
        self.clear_redo_stack()
        self.clear_undo_stack()

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

        # TODO: should this be placed here?
        self._action_executed()

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
                while len(self._undo_stack) > self._stack_depth:
                    del self._undo_stack[0]
            else:
                pass #log.debug('nothing to commit')

            self._current_transaction = None
        component.handle(UndoManagerStateChanged(self))
        self._action_executed()

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
        self._action_executed()

    def discard_transaction(self):

        if not self._current_transaction:
            raise TransactionError, 'No transaction to discard'

        self._transaction_depth -= 1
        if self._transaction_depth == 0:
            self._current_transaction = None
        component.handle(UndoManagerStateChanged(self))
        self._action_executed()

    @action(name='edit-undo', stock_id='gtk-undo', accel='<Control>z')
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
        self._action_executed()

    @action(name='edit-redo', stock_id='gtk-redo', accel='<Control>y')
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
        self._action_executed()

    def in_transaction(self):
        return self._current_transaction is not None

    def can_undo(self):
        return bool(self._current_transaction or self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)


    @component.adapter(ActionExecuted)
    def _action_executed(self, event=None):
        self.action_group.get_action('edit-undo').set_sensitive(self.can_undo())
        self.action_group.get_action('edit-redo').set_sensitive(self.can_redo())

    ##
    ## Undo Handlers
    ##

    def _undo_handler(self, event):
        self.add_undo_action(lambda: state.saveapply(*event));

    def _register_undo_handlers(self):
        self._app.register_handler(self.undo_create_event)
        self._app.register_handler(self.undo_delete_event)
        self._app.register_handler(self.undo_attribute_change_event)
        self._app.register_handler(self.undo_association_set_event)
        self._app.register_handler(self.undo_association_add_event)
        self._app.register_handler(self.undo_association_delete_event)

        #
        # Direct revert-statements from gaphas to the undomanager
        state.observers.add(state.revert_handler)

        state.subscribers.add(self._undo_handler)

    def _unregister_undo_handlers(self):
        self._app.unregister_handler(self.undo_create_event)
        self._app.unregister_handler(self.undo_delete_event)
        self._app.unregister_handler(self.undo_attribute_change_event)
        self._app.unregister_handler(self.undo_association_set_event)
        self._app.unregister_handler(self.undo_association_add_event)
        self._app.unregister_handler(self.undo_association_delete_event)

        from gaphas import state
        state.observers.discard(state.revert_handler)

        state.subscribers.discard(self._undo_handler)


    @component.adapter(IElementCreateEvent)
    def undo_create_event(self, event):
        factory = event.service
        element = event.element
        def _undo_create_event():
            try:
                del factory._elements[element.id]
            except KeyError:
                pass # Key was probably already removed in an unlink call
            component.handle(ElementDeleteEvent(factory, element))
        self.add_undo_action(_undo_create_event)


    @component.adapter(IElementDeleteEvent)
    def undo_delete_event(self, event):
        factory = event.service
        element = event.element
        def _undo_delete_event():
            factory._elements[element.id] = element
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
