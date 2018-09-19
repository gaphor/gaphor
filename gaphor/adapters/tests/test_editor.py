#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
from __future__ import absolute_import

import gtk

from gaphor.UML import uml2
from gaphor.adapters.propertypages import AttributesPage, OperationsPage
from gaphor.diagram import items
from gaphor.diagram.interfaces import IEditor
from gaphor.tests import TestCase


class EditorTestCase(TestCase):
    def setUp(self):
        super(EditorTestCase, self).setUp()

    def test_association_editor(self):
        assoc = self.create(items.AssociationItem)
        adapter = IEditor(assoc)
        assert not adapter.is_editable(10, 10)
        assert adapter._edit is None

        # Intermezzo: connect the association between two classes
        class1 = self.create(items.ClassItem, uml2.Class)
        class2 = self.create(items.ClassItem, uml2.Class)

        assoc.handles()[0].pos = 10, 10
        assoc.handles()[-1].pos = 100, 100
        self.connect(assoc, assoc.head, class1)
        self.connect(assoc, assoc.tail, class2)
        assert assoc.subject

        # Now the association has a subject member, so editing should really
        # work.
        pos = 55, 55
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc)

        pos = assoc.head_end._name_bounds[:2]
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc.head_end)

        pos = assoc.tail_end._name_bounds[:2]
        self.assertTrue(adapter.is_editable(*pos))
        self.assertTrue(adapter._edit is assoc.tail_end)

    def test_objectnode_editor(self):
        node = self.create(items.ObjectNodeItem, uml2.ObjectNode)
        self.diagram.canvas.update_now()

        adapter = IEditor(node)
        self.assertTrue(adapter.is_editable(10, 10))
        # assert not adapter.edit_tag

        # assert adapter.is_editable(*node.tag_bounds[:2])
        # assert adapter.edit_tag

    def test_classifier_editor(self):
        """
        Test classifier editor
        """
        klass = self.create(items.ClassItem, uml2.Class)
        klass.subject.name = 'Class1'

        self.diagram.canvas.update()

        attr = self.element_factory.create(uml2.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        oper = self.element_factory.create(uml2.Operation)
        oper.name = 'method'
        klass.subject.ownedOperation = oper

        self.diagram.canvas.update()

        edit = IEditor(klass)

        self.assertEqual('CompartmentItemEditor', edit.__class__.__name__)

        self.assertEqual(True, edit.is_editable(10, 10))

        # Test the inner working of the editor
        self.assertEqual(klass, edit._edit)
        self.assertEqual('Class1', edit.get_text())

        # The attribute:
        y = klass._header_size[1] + klass.style.compartment_padding[0] + 3
        self.assertEqual(True, edit.is_editable(4, y))
        self.assertEqual(attr, edit._edit.subject)
        self.assertEqual('+ blah', edit.get_text())

        y += klass.compartments[0].height
        # The operation
        self.assertEqual(True, edit.is_editable(3, y))
        self.assertEqual(oper, edit._edit.subject)
        self.assertEqual('+ method()', edit.get_text())

    def test_class_attribute_editor(self):
        klass = self.create(items.ClassItem, uml2.Class)
        klass.subject.name = 'Class1'

        editor = AttributesPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        self.assertSame(gtk.TreeView, type(tree_view))

        attr = self.element_factory.create(uml2.Property)
        attr.name = "blah"
        klass.subject.ownedAttribute = attr

        self.assertSame(attr, tree_view.get_model()[0][-1])
        self.assertEquals("+ blah", tree_view.get_model()[0][0])

        attr.name = "foo"
        self.assertEquals("+ foo", tree_view.get_model()[0][0])
        attr.typeValue = 'int'
        self.assertEquals("+ foo: int", tree_view.get_model()[0][0])
        attr.isDerived = True
        self.assertEquals("+ /foo: int", tree_view.get_model()[0][0])
        page.destroy()

    def test_class_operation_editor(self):
        klass = self.create(items.ClassItem, uml2.Class)
        klass.subject.name = 'Class1'

        editor = OperationsPage(klass)
        page = editor.construct()
        tree_view = page.get_children()[1]
        self.assertSame(gtk.TreeView, type(tree_view))

        oper = self.element_factory.create(uml2.Operation)
        oper.name = 'o'
        klass.subject.ownedOperation = oper

        self.assertSame(oper, tree_view.get_model()[0][-1])
        self.assertEquals("+ o()", tree_view.get_model()[0][0])
        p = self.element_factory.create(uml2.Parameter)
        p.name = 'blah'
        oper.formalParameter = p
        self.assertEquals("+ o(in blah)", tree_view.get_model()[0][0])

        page.destroy()

# vim:sw=4:et:ai
