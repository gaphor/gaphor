"""
Test extend item connections.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class ExtendItemTestCase(TestCase):
    def test_use_case_glue(self):
        """Test "extend" glueing to use cases
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        glued = self.allow(extend, extend.head, uc1)
        self.assertTrue(glued)


    def test_use_case_connect(self):
        """Test connecting "extend" to use cases
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)
        extend = self.create(items.ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.assertTrue(self.get_connected(extend.head), uc1)

        self.connect(extend, extend.tail, uc2)
        self.assertTrue(self.get_connected(extend.tail), uc2)


    def test_use_case_connect(self):
        """Test reconnecting use cases with "extend"
        """
        uc1 = self.create(items.UseCaseItem, UML.UseCase)
        uc2 = self.create(items.UseCaseItem, UML.UseCase)
        uc3 = self.create(items.UseCaseItem, UML.UseCase)
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
