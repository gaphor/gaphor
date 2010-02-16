
from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class SanitizerServiceTest(TestCase):

    services = TestCase.services + [ 'sanitizer' ]

    def test_presentation_delete(self):
        """
        Remove element if the last instance of an item is deleted.
        """
        ef = self.element_factory
        
        klassitem = self.create(items.ClassItem, UML.Class)
        klass = klassitem.subject

        assert klassitem.subject.presentation[0] is klassitem
        assert klassitem.canvas

        # Delete presentation here:

        klassitem.unlink()

        assert not klassitem.canvas
        assert klass not in self.element_factory.lselect()

# vim:sw=4:et:ai
