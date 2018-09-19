#!/usr/bin/env python

# Copyright (C) 2010-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for transactions in Gaphor."""

from __future__ import absolute_import

from unittest import TestCase

from gaphor.application import Application
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor.transaction import Transaction, TransactionError

begins = []
commits = []
rollbacks = []


def handle_begins(event):
    """Store TransactionBegin events in begins."""
    begins.append(event)


def handle_commits(event):
    """Store TransactionCommit events in commits."""
    commits.append(event)


def handle_rollback(event):
    """Store TransactionRollback events in rollbacks."""
    rollbacks.append(event)


class TransactionTestCase(TestCase):
    """Test case for transactions with the component registry 
    enabled."""

    def setUp(self):
        """Initialize Gaphor services and register transaction event
        handlers."""

        Application.init(services=['component_registry'])

        component_registry = Application.get_service('component_registry')

        component_registry.register_handler(handle_begins, [TransactionBegin])
        component_registry.register_handler(handle_commits, [TransactionCommit])
        component_registry.register_handler(handle_rollback, [TransactionRollback])

        del begins[:]
        del commits[:]
        del rollbacks[:]

    def tearDown(self):
        """Finished with the test case.  Unregister event handlers that
        store transaction events."""

        component_registry = Application.get_service('component_registry')

        component_registry.unregister_handler(handle_begins, [TransactionBegin])
        component_registry.unregister_handler(handle_commits, [TransactionCommit])
        component_registry.unregister_handler(handle_rollback, [TransactionRollback])

    def test_transaction_commit(self):
        """Test committing a transaction."""

        tx = Transaction()

        self.assertTrue(tx._stack, 'Transaction has no stack')
        self.assertEquals(1, len(begins), 'Incorrect number of TrasactionBegin events')
        self.assertEquals(0, len(commits), 'Incorrect number of TransactionCommit events')
        self.assertEquals(0, len(rollbacks), 'Incorrect number of TransactionRollback events')

        tx.commit()

        self.assertEquals(1, len(begins), 'Incorrect number of TrasactionBegin events')
        self.assertEquals(1, len(commits), 'Incorrect number of TransactionCommit events')
        self.assertEquals(0, len(rollbacks), 'Incorrect number of TransactionRollback events')
        self.assertFalse(tx._stack, 'Transaction stack is not empty')

        try:
            tx.commit()
        except TransactionError:
            pass
        else:
            self.fail('Commit should not have succeeded')

    def test_transaction_rollback(self):
        """Test rolling back a transaction."""

        tx = Transaction()

        self.assertTrue(tx._stack, 'Transaction has no stack')
        self.assertEquals(1, len(begins), 'Incorrect number of TrasactionBegin events')
        self.assertEquals(0, len(commits), 'Incorrect number of TransactionCommit events')
        self.assertEquals(0, len(rollbacks), 'Incorrect number of TransactionRollback events')

        tx.rollback()

        self.assertEquals(1, len(begins), 'Incorrect number of TrasactionBegin events')
        self.assertEquals(0, len(commits), 'Incorrect number of TransactionCommit events')
        self.assertEquals(1, len(rollbacks), 'Incorrect number of TransactionRollback events')

        self.assertFalse(tx._stack, 'Transaction stack is not empty')

    def test_transaction_commit_after_rollback(self):
        """Test committing one transaction after rolling back another
        transaction."""

        tx1 = Transaction()
        tx2 = Transaction()

        tx2.rollback()
        tx1.commit()

        self.assertEquals(1, len(begins), 'Incorrect number of TrasactionBegin events')
        self.assertEquals(0, len(commits), 'Incorrect number of TransactionCommit events')
        self.assertEquals(1, len(rollbacks), 'Incorrect number of TransactionRollback events')

    def test_transaction_stack(self):
        """Test the transaction stack."""

        tx1 = Transaction()
        tx2 = Transaction() # tx2 is used despite warnings

        try:
            tx1.commit()
        except TransactionError:
            pass
        else:
            self.fail('Commit should not have succeeded')

    def test_transaction_context(self):
        """Test the transaction context manager."""

        with Transaction() as tx:
            self.assertTrue(isinstance(tx, Transaction), 'Context is not a Transaction instance')
            self.assertTrue(Transaction._stack, 'Transaction instance has no stack inside a context')

        self.assertFalse(Transaction._stack, 'Transaction stack should be empty')

    def test_transaction_context_error(self):
        """Test the transaction context manager with errors."""

        try:
            with Transaction():
                raise TypeError('transaction error')
        except TypeError as e:
            self.assertEquals('transaction error', str(e), 'Transaction context manager did no raise correct exception')
        else:
            self.fail('Transaction context manager did not raise exception when it should have')


class TransactionWithoutComponentRegistryTestCase(TestCase):
    """Test case for transactions with no component registry."""

    def test_transaction(self):
        """Test basic transaction functionality."""

        tx = Transaction()
        tx.rollback()

        tx = Transaction()
        tx.commit()
