#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
"""
Unit tests for AssociationItem.
"""

from __future__ import absolute_import
from __future__ import print_function
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram.items import AssociationItem, ClassItem


class AssociationItemTestCase(TestCase):

    services = TestCase.services + ['element_dispatcher']

    def setUp(self):
        super(AssociationItemTestCase, self).setUp()
        self.assoc = self.create(AssociationItem)
        self.class1 = self.create(ClassItem, uml2.Class)
        self.class2 = self.create(ClassItem, uml2.Class)


    def test_create(self):
        """Test association creation and its basic properties
        """
        self.connect(self.assoc, self.assoc.head, self.class1)
        self.connect(self.assoc, self.assoc.tail, self.class2)

        self.assertTrue(isinstance(self.assoc.subject, uml2.Association))
        self.assertTrue(self.assoc.head_end.subject is not None)
        self.assertTrue(self.assoc.tail_end.subject is not None)

        self.assertFalse(self.assoc.show_direction)

        self.assoc.show_direction = True
        self.assertTrue(self.assoc.show_direction)


    def test_invert_direction(self):
        """Test association direction inverting
        """
        self.connect(self.assoc, self.assoc.head, self.class1)
        self.connect(self.assoc, self.assoc.tail, self.class2)

        head_subject = self.assoc.subject.memberEnd[0]
        tail_subject = self.assoc.subject.memberEnd[1]

        self.assoc.invert_direction()

        self.assertTrue(head_subject is self.assoc.subject.memberEnd[1])
        self.assertTrue(tail_subject is self.assoc.subject.memberEnd[0])


    def test_association_end_updates(self):
        """Test association end navigability connected to a class"""
        from gaphas.canvas import Canvas
        canvas = Canvas()
        c1 = self.create(ClassItem, uml2.Class)
        c2 = self.create(ClassItem, uml2.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, c1)
        c = self.get_connected(a.head)
        self.assertTrue(c is c1)

        self.connect(a, a.tail, c2)
        c = self.get_connected(a.tail)
        self.assertTrue(c is c2)

        assert a.subject.memberEnd, a.subject.memberEnd

        assert a.subject.memberEnd[0] is a.head_end.subject
        assert a.subject.memberEnd[1] is a.tail_end.subject
        assert a.subject.memberEnd[0].name is None

        dispatcher = self.get_service('element_dispatcher')
        print((a.subject.memberEnd[0], uml2.Property.name) in dispatcher._handlers)
        print('*' * 60)
        a.subject.memberEnd[0].name = 'blah'
        print('*' * 60)
        self.diagram.canvas.update()

        assert a.head_end._name == '+ blah', a.head_end.get_name()

    def test_association_orthogonal(self):
        c1 = self.create(ClassItem, uml2.Class)
        c2 = self.create(ClassItem, uml2.Class)
        a = self.create(AssociationItem)

        self.connect(a, a.head, c1)
        c = self.get_connected(a.head)
        self.assertTrue(c is c1)

        a.matrix.translate(100, 100)
        self.connect(a, a.tail, c2)
        c = self.get_connected(a.tail)
        self.assertTrue(c is c2)

        try:
            a.orthogonal = True
        except ValueError:
            pass # Expected, hanve only 2 handles, need 3 or more
        else:
            assert False, 'Can not set line to orthogonal with less than 3 handles'

# vim:sw=4:et:ai
