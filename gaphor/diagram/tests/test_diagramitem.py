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
