"""
Test include item connections.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests import TestCase


class IncludeItemTestCase(TestCase):
    def test_use_case_glue(self):
        """Test "include" glueing to use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        include = self.create(items.IncludeItem)

        glued = self.allow(include, include.head, uc1)
        self.assertTrue(glued)

    def test_use_case_connect(self):
        """Test connecting "include" to use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        include = self.create(items.IncludeItem)

        self.connect(include, include.head, uc1)
        self.assertTrue(self.get_connected(include.head), uc1)

        self.connect(include, include.tail, uc2)
        self.assertTrue(self.get_connected(include.tail), uc2)

    def test_use_case_connect(self):
        """Test reconnecting use cases with "include"
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        uc3 = self.create(items.UseCaseItem, uml2.UseCase)
        include = self.create(items.IncludeItem)

        # connect: uc1 -> uc2
        self.connect(include, include.head, uc1)
        self.connect(include, include.tail, uc2)
        e = include.subject

        # reconnect: uc1 -> uc2
        self.connect(include, include.tail, uc3)

        self.assertSame(e, include.subject)
        self.assertSame(include.subject.addition, uc1.subject)
        self.assertSame(include.subject.includingCase, uc3.subject)

    def test_use_case_disconnect(self):
        """Test disconnecting "include" from use cases
        """
        uc1 = self.create(items.UseCaseItem, uml2.UseCase)
        uc2 = self.create(items.UseCaseItem, uml2.UseCase)
        include = self.create(items.IncludeItem)

        self.connect(include, include.head, uc1)
        self.connect(include, include.tail, uc2)

        self.disconnect(include, include.head)
        self.assertTrue(self.get_connected(include.head) is None)
        self.assertTrue(include.subject is None)

        self.disconnect(include, include.tail)
        self.assertTrue(self.get_connected(include.tail) is None)

# vim:sw=4:et:ai
