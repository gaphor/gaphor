
from __future__ import absolute_import
from gaphor.tests.testcase import TestCase
from gaphor.storage.verify import orphan_references
from gaphor.UML import uml2


class VerifyTestCase(TestCase):

    def test_verifier(self):
        factory = self.element_factory
        c = factory.create(uml2.Class)
        p = factory.create(uml2.Property)
        c.ownedAttribute = p

        assert not orphan_references(factory)

        # Now create a separate item, not part of the factory:

        m = uml2.Comment(id="acd123")
        m.annotatedElement = c
        assert m in c.ownedComment

        assert orphan_references(factory)


# vim:sw=4:et:ai
