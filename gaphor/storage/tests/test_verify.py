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
from gaphor.tests.testcase import TestCase
from gaphor.storage.verify import orphan_references
from gaphor.UML import uml2


class VerifyTestCase(TestCase):

    def test_verifier(self):
        factory = self.element_factory
        c = factory.create(uml2.Class)
        p = factory.create(uml2.Property)
        c.ownedAttribute = p

        assert not orphan_references(factory)

        # Now create a separate item, not part of the factory:

        m = uml2.Comment(id="acd123")
        m.annotatedElement = c
        assert m in c.ownedComment

        assert orphan_references(factory)


# vim:sw=4:et:ai
