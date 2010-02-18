
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

        self.assertTrue(klassitem.subject.presentation[0] is klassitem)
        self.assertTrue(klassitem.canvas is not None)

        # Delete presentation here:

        klassitem.unlink()

        self.assertTrue(not klassitem.canvas)
        self.assertTrue(klass not in self.element_factory.lselect())


    def test_stereotype_attribute_delete(self):
        factory = self.element_factory
        create = factory.create
        
        # Set the stage
        #metaklass = create(UML.Class)
        #metaklass.name = 'Class'
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        #ext = UML.model.create_extension(factory, metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(factory, klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        # Now, what happens if the attribute is deleted:
        self.assertTrue(st_attr in stereotype.ownedMember)
        self.assertTrue(slot in instspec.slot)

        st_attr.unlink()

        self.assertEquals([], list(stereotype.ownedMember))
        self.assertEquals([], list(instspec.slot))

# vim:sw=4:et:ai
