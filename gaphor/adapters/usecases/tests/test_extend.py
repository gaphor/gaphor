#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
"""
Test extend item connections.
"""

from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2
from gaphor.diagram import items

class ExtendItemTestCase(TestCase):
    def test_use_case_glue(self):
        """Test "extend" glueing to use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        extend = self.create(items.ExtendItem)

        glued = self.allow(extend, extend.head, uc1)
        self.assertTrue(glued)


    def test_use_case_connect(self):
        """Test connecting "extend" to use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        extend = self.create(items.ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.assertTrue(self.get_connected(extend.head), uc1)

        self.connect(extend, extend.tail, uc2)
        self.assertTrue(self.get_connected(extend.tail), uc2)


    def test_use_case_connect(self):
        """Test reconnecting use cases with "extend"
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        uc3 = self.create(items.UseCaseItem, uml2.UseCase)
        extend = self.create(items.ExtendItem)

        # connect: uc1 -> uc2
        self.connect(extend, extend.head, uc1)
        self.connect(extend, extend.tail, uc2)
        e = extend.subject

        # reconnect: uc1 -> uc2
        self.connect(extend, extend.tail, uc3)

        self.assertSame(e, extend.subject)
        self.assertSame(extend.subject.extendedCase, uc1.subject)
        self.assertSame(extend.subject.extension, uc3.subject)


    def test_use_case_disconnect(self):
        """Test disconnecting "extend" from use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        extend = self.create(items.ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.connect(extend, extend.tail, uc2)

        self.disconnect(extend, extend.head)
        self.assertTrue(self.get_connected(extend.head) is None)
        self.assertTrue(extend.subject is None)

        self.disconnect(extend, extend.tail)
        self.assertTrue(self.get_connected(extend.tail) is None)



# vim:sw=4:et:ai
