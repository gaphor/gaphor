# Undo Manager

Undo is a required feature in modern applications. Gaphor is no exception.
Having an undo function in place means you can change the model and easily revert
to an older state.

## Overview of Transactions

The recording and playback of changes in Gaphor is handled by the the Undo
Manager. The Undo Manager works transactionally.
A transaction must succeed or fail as a complete unit. If
the transaction fails in the middle, it is rolled back. In Gaphor this is
achieved by the `transaction` module, which provides a context manager `Transaction` and
a decorator called `@transactional`.

When transactions take place, they emit event notifications on the key
transaction milestones so that other services can make use of the events. The
event notifications are for the begin of the transaction, and the commit of the
transaction if it is successful or the rollback of the transaction if it fails.

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
2.  The `UndoManager` plays back all the recorded actions, but does not store it.


## References

- [A Framework for Undoing Actions in Collaborative
Systems](http://web.eecs.umich.edu/~aprakash/papers/undo-tochi94.pdf)
- [Undoing Actions in Collaborative Work: Framework and
Experience](https://www.eecs.umich.edu/techreports/cse/94/CSE-TR-196-94.pdf)
- [Implementing a Selective Undo Framework in
Python](https://legacy.python.org/workshops/1997-10/proceedings/zukowski.html)
