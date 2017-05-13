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
from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.services.copyservice import CopyService
from gaphor.application import Application
from gaphor.tests.testcase import TestCase


class CopyServiceTestCase(TestCase):

    services = TestCase.services + ['main_window', 'action_manager', 'properties', 'undo_manager', 'ui_manager']

    def test_init(self):
        service = CopyService()
        service.init(Application)
        # No exception? ok!

    def test_copy(self):
        service = CopyService()
        service.init(Application)

        ef = self.element_factory
        diagram = ef.create(uml2.Diagram)
        ci = diagram.create(items.CommentItem, subject=ef.create(uml2.Comment))

        service.copy([ci])
        assert diagram.canvas.get_all_items() == [ ci ]

        service.paste(diagram)

        assert len(diagram.canvas.get_all_items()) == 2, diagram.canvas.get_all_items()
    
    def test_copy_named_item(self):
        service = CopyService()
        service.init(Application)

        ef = self.element_factory
        diagram = ef.create(uml2.Diagram)
        c = diagram.create(items.ClassItem, subject=ef.create(uml2.Class))

        c.subject.name = 'Name'

        import gobject
        self.assertEquals(0, gobject.main_depth())

        diagram.canvas.update_now()
        i = list(diagram.canvas.get_all_items())
        self.assertEquals(1, len(i), i)
        self.assertEquals('Name', i[0]._name.text)

        service.copy([c])
        assert diagram.canvas.get_all_items() == [ c ]

        service.paste(diagram)

        i = diagram.canvas.get_all_items()

        self.assertEquals(2, len(i), i)

        diagram.canvas.update_now()

        self.assertEquals('Name', i[0]._name.text)
        self.assertEquals('Name', i[1]._name.text)


    def _skip_test_copy_paste_undo(self):
        """
        Test if copied data is undoable.
        """
        from gaphor.storage.verify import orphan_references

        service = CopyService()
        service.init(Application)

        # Setting the stage:
        ci1 = self.create(items.ClassItem, uml2.Class)
        ci2 = self.create(items.ClassItem, uml2.Class)
        a = self.create(items.AssociationItem)

        self.connect(a, a.head, ci1)
        self.connect(a, a.tail, ci2)

        self.assertTrue(a.subject)
        self.assertTrue(a.head_end.subject)
        self.assertTrue(a.tail_end.subject)

        # The act: copy and paste, perform undo afterwards
        service.copy([ci1, ci2, a])

        service.paste(self.diagram)

        all_items = list(self.diagram.canvas.get_all_items())

        self.assertEquals(6, len(all_items))
        self.assertFalse(orphan_references(self.element_factory))

        self.assertSame(all_items[0].subject, all_items[3].subject)
        self.assertSame(all_items[1].subject, all_items[4].subject)
        self.assertSame(all_items[2].subject, all_items[5].subject)

        undo_manager = self.get_service('undo_manager')

        undo_manager.undo_transaction()

        self.assertEquals(3, len(self.diagram.canvas.get_all_items()))
        self.assertFalse(orphan_references(self.element_factory))


# vim:sw=4:et:ai
