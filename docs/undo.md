# Undo Manager

Fine grained undo: undo specific properties.

Add undo-operation, e.g. Item.request_update() should be executed as
part of an undo action. Such actions are normally called after the
properties have been set right though. This is not a problem for idle
tasks, but for directly executed tasks it is.

Should only need to save the originals, values calculated, e.g. during
an update shouldn't have to be calculated -> use undo-operations to
trigger updates.

To update:

> Handle:
>
> :   x, y (solvable) connectable (attr) visible (attr) movable (attr)
>     connection status (solver?)
>
> Item:
>
> :   matrix canvas is managed from Canvas
>
>     Element:
>
>     :   handles width, height min_width, min_height (solvable?)
>
>     Line:
>
>     :   handles line_width fuzzyness (attr) orthogonal (boolean)
>         horizontal (boolean)
>
> Canvas:
>
> :   
>
>     tree:
>
>     :   add() remove()
>
>     request_update() (should be performed as part of undo action when
>     called)
>
> Solver (?):
>
> :   add_constraint() remove_constraint() Variable state
>
In Gaphor, connecting two diagram items is considered an atomic task,
performed by a IConnect adapter. This operation results in a set of
primitive tasks (properties set and a constraint created).

For methods, it should be possible to create a decorator (@reversible)
that schedules a method with the same signature as the calling
operation, but with the inverse effect (e.g. the gaphas.tree module):

    class Tree:

      @reversable(lambda s, n, p: s.remove(n))
      def add(self, node, parent=None):
          ... add

      @reversable(add, self='self', node='node', parent='self.get_parent(node)')
      def remove(self, node):
          ... remove

Okay, so the second case is tougher...

So what we did: Add a StateManager to gaphas. All changes are sent to
the statemanager. Gaphor should implement its own state manager.

-   all state changes can easily be recorded
-   fix it in one place
-   reusable throughout Gaphas and subtypes.

## Transactions

Gaphor's Undo manager works transactionally. Typically, methods can be
decorated with @transactional and undo data is stored in the current
transaction. A new tx is created when none exists.

Although undo functionality is at the core of Gaphor (diagram items and
model elements have been adapted to provide proper undo information),
the UndoManager itself is just a service.

Transaction support though is a real core functionality. By letting
elements and items emit event notifications on important changed other
(yet to be defined) services can take benefit of those events. The UML
module already works this way. Gaphas (the Gaphor canvas) also emits
state changes.

When state changes happen in model elements and diagram items an event
is emitted. Those events are handled by special handlers that produce
\"reverse-events\". Reverse events are functions that perform exactly
the opposite operation. Those functions are stored in a list (which
technically is the Transaction). When an undo request is done the list
is executed in LIFO order.

To start a transaction:

1.  A Transaction object has been created.
2.  This results in the emission of a TransactionBegin event.
3.  The TransactionBegin event is a trigger for the UndoManager to start
    listening for IUndoEvent actions.

Now, that should be done when a model element or diagram item sends a
state change:

1.  The event is handled by the \"reverse-handler\"
2.  Reverse handler generates a IUndoEvent signal
3.  The signal is received and stored as part of the undo-transaction.

(Maybe step 2 and 3 can be merged, since only one function is not of any
interest to the rest of the application - creates nasty dependencies)

If nested transaction are created a simple counter is incremented.

When the topmost Transaction is committed:

1.  A TransactionCommit event is emitted
2.  This triggers the UndoManager to close and store the transaction.

When a transaction is rolled back:

1.  The main transaction is marked for rollback
2.  When the toplevel tx is rolled back or committed a
    TransactionRollback event is emitted
3.  This triggers the UndoManager to play back all recorded actions and
    stop listening.

## References

- [A Framework for Undoing Actions in Collaborative Systems](http://web.eecs.umich.edu/~aprakash/papers/undo-tochi94.pdf)
- [Undoing Actions in Collaborative Work: Framework and Experience](https://www.eecs.umich.edu/techreports/cse/94/CSE-TR-196-94.pdf)
- [Implementing a Selective Undo Framework in Python](https://legacy.python.org/workshops/1997-10/proceedings/zukowski.html)
