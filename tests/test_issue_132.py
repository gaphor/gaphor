#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.core import transactional
from gaphor.tests import TestCase
from gaphor.ui.namespace import NamespaceModel


class UndoRedoBugTestCase(TestCase):
    services = TestCase.services + ['undo_manager']

    def setUp(self):
        super(UndoRedoBugTestCase, self).setUp()
        self.undo_manager = self.get_service('undo_manager')
        self.namespace = NamespaceModel(self.element_factory)

    @transactional
    def create_with_attribute(self):
        self.class_ = self.element_factory.create(uml2.Class)
        self.attribute = self.element_factory.create(uml2.Property)
        self.class_.ownedAttribute = self.attribute

    # Fix:  Remove operation should be transactional ;)
    @transactional
    def remove_attribute(self):
        self.attribute.unlink()

    def test_bug_with_attribute(self):
        """
        Does not trigger the error.
        """
        self.create_with_attribute()
        assert len(self.class_.ownedAttribute) == 1
        assert self.attribute.namespace is self.class_, self.attribute.namespace

        self.remove_attribute()
        assert len(self.class_.ownedAttribute) == 0
        assert self.attribute.namespace is None

        self.undo_manager.undo_transaction()

        assert self.attribute in self.class_.ownedAttribute

        self.undo_manager.redo_transaction()

# vi:sw=4:et:ai
