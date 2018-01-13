#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test basic diagram item functionality like styles, etc.
"""

from __future__ import absolute_import
import unittest
from gaphor.diagram.diagramitem import DiagramItem

class ItemTestCase(unittest.TestCase):
    def setUp(self):
        class ItemA(DiagramItem):
            __style__ = {
                'a-01': 1,
                'a-02': 2,
            }
        self.ItemA = ItemA

    def test_style_assign(self):
        """
        Test style assign
        """
        item_a = self.ItemA()
        self.assertEqual(self.ItemA.style.a_01, 1)
        self.assertEqual(self.ItemA.style.a_02, 2)
        self.assertEqual(item_a.style.a_01, 1)
        self.assertEqual(item_a.style.a_02, 2)


    def test_style_override(self):
        """
        Test style override
        """

        class ItemB(self.ItemA):
            __style__ = {
                'b-01': 3,
                'b-02': 4,
                'a-01': 5,
            }
        item_b = ItemB()
        self.assertEqual(ItemB.style.b_01, 3)
        self.assertEqual(ItemB.style.b_02, 4)
        self.assertEqual(ItemB.style.a_01, 5)
        self.assertEqual(ItemB.style.a_02, 2)
        self.assertEqual(item_b.style.b_01, 3)
        self.assertEqual(item_b.style.b_02, 4)
        self.assertEqual(item_b.style.a_01, 5)
        self.assertEqual(item_b.style.a_02, 2)

        # check ItemA style, it should remaing unaffected by ItemB style
        # changes
        self.assertEqual(self.ItemA.style.a_01, 1)
        self.assertEqual(self.ItemA.style.a_02, 2)
