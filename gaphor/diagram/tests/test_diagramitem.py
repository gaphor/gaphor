"""
Test basic diagram item functionality like styles, etc.
"""

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
        self.assertEqual(self.ItemA.styles.a_01, 1)
        self.assertEqual(self.ItemA.styles.a_02, 2)
        self.assertEqual(item_a.styles.a_01, 1)
        self.assertEqual(item_a.styles.a_02, 2)


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
        self.assertEqual(ItemB.styles.b_01, 3)
        self.assertEqual(ItemB.styles.b_02, 4)
        self.assertEqual(ItemB.styles.a_01, 5)
        self.assertEqual(ItemB.styles.a_02, 2)
        self.assertEqual(item_b.styles.b_01, 3)
        self.assertEqual(item_b.styles.b_02, 4)
        self.assertEqual(item_b.styles.a_01, 5)
        self.assertEqual(item_b.styles.a_02, 2)
