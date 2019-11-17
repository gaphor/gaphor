# Undo Manager

Undo is implemented in order to erase the last change done, reverting it to an
older state or reversing the command that was done to the model being edited.
With the possibility of undo, users can explore and work without fear of making
mistakes, because they can easily be undone.

Gaphor makes use of the [undo
system](https://gaphas.readthedocs.io/en/latest/undo.html) in Gaphas, which is
Gaphor's Canvas widget. Gaphas implements this undo system by storing the
reverse operations to an undo list. For example, if you add a new item to the
screen, it will save the remove operation to the undo list. If undo is then
called, Gaphas will then remove the item from the screen that was added.

## Overview of Transactions

Gaphor adds on to what Gaphas provides with an undo service, called the Undo
Manager. The Undo Manager works transactionally. This means that if something is
being updated by the user in a model, each change is divided into operations
called transactions. Each operation must succeed or fail as a complete unit. If
the transaction fails in the middle, it is rolled back. In Gaphor this is
achieved by the `transaction` module, which provides a decorator called
`@transactional`. Methods then make use of this decorator, and the undo data is
stored in a transaction once the method is called. For example, pasting data in
the model using the `copyservice` module and setting a value on an object's
property page both create new transactions.

When transactions take place, they also emit event notifications on the key
transaction milestones so that other services can make use of the events. The
event notifications are for the begin of the transaction, and the commit of the
transaction if it is successful or the rollback of the transaction if it fails.
Please see the next sections for more detail on how these event notifications
work during a transaction.

## Start of a Transaction

1. A `Transaction` object is created.
2. `TransactionBegin` event is emitted.
3. The `UndoManager` instantiates a new `ActionStack` which is the transaction
   object, and adds the undo action to the stack. 

Nested transactions are supported to allow a transaction to be added
inside of another transaction that is already in progress.

## Successful Transaction

1.  A `TransactionCommit` event is emitted
2.  The `UndoManager` closes and stores the transaction.

## Failed Transaction

1.  A `TransactionRollback` event is emitted.
    TransactionRollback event is emitted
2.  The `UndoManager` plays back all the recorded actions and
    then stops listening.


## References

- [A Framework for Undoing Actions in Collaborative
Systems](http://web.eecs.umich.edu/~aprakash/papers/undo-tochi94.pdf)
- [Undoing Actions in Collaborative Work: Framework and
Experience](https://www.eecs.umich.edu/techreports/cse/94/CSE-TR-196-94.pdf)
- [Implementing a Selective Undo Framework in
Python](https://legacy.python.org/workshops/1997-10/proceedings/zukowski.html)
