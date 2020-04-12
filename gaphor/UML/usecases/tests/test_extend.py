"""
Test extend item connections.
"""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.usecases.extend import ExtendItem
from gaphor.UML.usecases.usecase import UseCaseItem


class ExtendItemTestCase(TestCase):
    def test_use_case_glue(self):
        """Test "extend" gluing to use cases."""

        uc1 = self.create(UseCaseItem, UML.UseCase)
        extend = self.create(ExtendItem)

        glued = self.allow(extend, extend.head, uc1)
        assert glued

    def test_use_case_connect(self):
        """Test connecting "extend" to use cases
        """
        uc1 = self.create(UseCaseItem, UML.UseCase)
        uc2 = self.create(UseCaseItem, UML.UseCase)
        extend = self.create(ExtendItem)

        self.connect(extend, extend.head, uc1)
        assert self.get_connected(extend.head), uc1

        self.connect(extend, extend.tail, uc2)
        assert self.get_connected(extend.tail), uc2

    def test_use_case_reconnect(self):
        """Test reconnecting use cases with "extend"
        """
        uc1 = self.create(UseCaseItem, UML.UseCase)
        uc2 = self.create(UseCaseItem, UML.UseCase)
        uc3 = self.create(UseCaseItem, UML.UseCase)
        extend = self.create(ExtendItem)

        # connect: uc1 -> uc2
        self.connect(extend, extend.head, uc1)
        self.connect(extend, extend.tail, uc2)
        e = extend.subject

        # reconnect: uc1 -> uc2
        self.connect(extend, extend.tail, uc3)

        assert e is extend.subject
        assert extend.subject.extendedCase is uc1.subject
        assert extend.subject.extension is uc3.subject

    def test_use_case_disconnect(self):
        """Test disconnecting "extend" from use cases
        """
        uc1 = self.create(UseCaseItem, UML.UseCase)
        uc2 = self.create(UseCaseItem, UML.UseCase)
        extend = self.create(ExtendItem)

        self.connect(extend, extend.head, uc1)
        self.connect(extend, extend.tail, uc2)

        self.disconnect(extend, extend.head)
        assert self.get_connected(extend.head) is None
        assert extend.subject is None

        self.disconnect(extend, extend.tail)
        assert self.get_connected(extend.tail) is None
