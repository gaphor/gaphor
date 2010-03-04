
from unittest import TestCase 
from zope.component.globalregistry import base
from gaphor.transaction import Transaction, transactional, TransactionError
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback

begins = []
commits = []
rollbacks = []

def handle_begins(ev):
    begins.append(ev)

def handle_commits(ev):
    commits.append(ev)

def handle_rollback(ev):
    rollbacks.append(ev)


class TransactionTestCase(TestCase):

    def setUp(self):
        base.registerHandler(handle_begins, [TransactionBegin], event=False)
        base.registerHandler(handle_commits, [TransactionCommit], event=False)
        base.registerHandler(handle_rollback, [TransactionRollback], event=False)
        del begins[:]
        del commits[:]
        del rollbacks[:]
        assert not begins
        assert not commits
        assert not rollbacks


    def tearDown(self):
        base.unregisterHandler(handle_begins, [TransactionBegin])
        base.unregisterHandler(handle_commits, [TransactionCommit])
        base.unregisterHandler(handle_rollback, [TransactionRollback])


    def test_transaction_commit(self):
        tx = Transaction()
        self.assertTrue(tx._stack)
        self.assertEquals(1, len(begins))
        self.assertEquals(0, len(commits))
        self.assertEquals(0, len(rollbacks))

        tx.commit()
        self.assertEquals(1, len(begins))
        self.assertEquals(1, len(commits))
        self.assertEquals(0, len(rollbacks))

        self.assertFalse(tx._stack)

        try:
            tx.commit()
        except TransactionError:
            pass # ok
        else:
            assert False, 'should not be reached'


    def test_transaction_rollback(self):
        tx = Transaction()
        self.assertTrue(tx._stack)
        self.assertEquals(1, len(begins))
        self.assertEquals(0, len(commits))
        self.assertEquals(0, len(rollbacks))

        tx.rollback()
        self.assertEquals(1, len(begins))
        self.assertEquals(0, len(commits))
        self.assertEquals(1, len(rollbacks))

        self.assertFalse(tx._stack)


    def test_transaction_commit_after_rollback(self):
        tx = Transaction()
        tx2 = Transaction()

        tx2.rollback()

        tx.commit()
        self.assertEquals(1, len(begins))
        self.assertEquals(0, len(commits))
        self.assertEquals(1, len(rollbacks))


    def test_transaction_stack(self):
        tx = Transaction()
        tx2 = Transaction()

        try:
            tx.commit()
        except TransactionError, e:
            self.assertEquals('Transaction on stack is not the transaction being closed.', str(e))
        else:
            assert False, 'should not be reached'


    def test_transaction_context(self):
        with Transaction as tx:
            self.assertTrue(isinstance(tx, Transaction))
            self.assertTrue(Transaction._stack)
        self.assertFalse(Transaction._stack)


    def test_transaction_context_error(self):
        try:
            with Transaction:
                self.assertTrue(Transaction._stack)
                raise TypeError('some error')
        except TypeError, e:
            self.assertEquals('some error', str(e))
            self.assertFalse(Transaction._stack)
        else:
            self.assertFalse(Transaction._stack)
            assert False, 'should not be reached'


# vim:sw=4:et:ai
