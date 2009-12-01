"""
Test extend item connections.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class ExtendItemTestCase(TestCase):
    def test_use_case_glue(self):
        """Test glueing to use cases.
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        glued = self.allow(extend, extend.head, uc1)
        self.assertTrue(glued)


    def test_use_case_connect(self):
        """Test connecting to use cases.
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.assertTrue(self.get_connected(extend.head), uc1)

        self.connect(extend, extend.tail, uc2)
        self.assertTrue(self.get_connected(extend.tail), uc2)


    def test_use_case_disconnect(self):
        """Test disconnecting from use cases.
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.connect(extend, extend.tail, uc2)

        self.disconnect(extend, extend.head)
        self.assertTrue(self.get_connected(extend.head) is None)
        self.assertTrue(extend.subject is None)

        self.disconnect(extend, extend.tail)
        self.assertTrue(self.get_connected(extend.tail) is None)



# vim:sw=4:et:ai
