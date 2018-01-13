#!/usr/bin/env python

# Copyright (C) 2010-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase


class GaphasTest(TestCase):
    services = TestCase.services + ['sanitizer_service', 'undo_manager']

    def test_remove_class_with_association(self):
        c1 = self.create(items.ClassItem, uml2.Class)
        c1.name = 'klassitem1'
        c2 = self.create(items.ClassItem, uml2.Class)
        c2.name = 'klassitem2'

        a = self.create(items.AssociationItem)

        assert 3 == len(self.diagram.canvas.get_all_items())

        self.connect(a, a.head, c1)
        self.connect(a, a.tail, c2)

        assert a.subject
        assert self.element_factory.lselect(lambda e: e.isKindOf(uml2.Association))[0] is a.subject

        c1.unlink()

        self.diagram.canvas.update_now()

# vim:sw=4:et:ai
