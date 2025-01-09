Undo Manager
============

Undo is a required feature in modern applications. Gaphor is no exception.
Having an undo function in place means you can change the model and easily revert
to an older state.

Overview of Transactions
------------------------

The recording and playback of changes in Gaphor is handled by the the Undo
Manager. The Undo Manager works transactionally.
A transaction must succeed or fail as a complete unit. If
the transaction fails in the middle, it is rolled back. In Gaphor this is
achieved by the :mod:`~gaphor.transaction` module, which provides a context manager
:obj:`~gaphor.transaction.Transaction`.

When transactions take place, they emit events when the top-most transaction begins and is finished.
The event notifications are for the begin of the transaction, and the commit of the
transaction if it is successful or the rollback of the transaction if it fails.

The Undo Manager only allows changes to be made in a transaction. If a change is made outside
a transaction, an exception is raised.

Start of a Transaction
----------------------

1. A ``Transaction`` object is created.
2. ``TransactionBegin`` event is emitted.
3. The ``UndoManager`` instantiates a new ``ActionStack`` which is the transaction
   object, and adds the undo action to the stack.

Nested transactions are supported to allow a transaction to be added
inside of another transaction that is already in progress.

Successful Transaction
----------------------

1.  A ``TransactionCommit`` event is emitted
2.  The ``UndoManager`` closes and stores the transaction.

Failed Transaction
------------------

1.  A ``TransactionRollback`` event is emitted.
2.  The ``UndoManager`` plays back all the recorded actions, but does not store it.


Transaction API
---------------

.. note::

   You only require transactions if the undo manager is active.


.. autoclass:: gaphor.transaction.Transaction
   :members:

.. autoclass:: gaphor.event.TransactionBegin

.. autoclass:: gaphor.event.TransactionCommit

.. autoclass:: gaphor.event.TransactionRollback

References
----------

* `A Framework for Undoing Actions in Collaborative Systems <http://web.eecs.umich.edu/~aprakash/papers/undo-tochi94.pdf>`_
* `Undoing Actions in Collaborative Work: Framework and Experience <https://www.eecs.umich.edu/techreports/cse/94/CSE-TR-196-94.pdf>`_
* `Implementing a Selective Undo Framework in Python <https://legacy.python.org/workshops/1997-10/proceedings/zukowski.html>`_
