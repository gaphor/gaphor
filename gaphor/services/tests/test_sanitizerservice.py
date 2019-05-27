from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.classes import ClassItem


class SanitizerServiceTest(TestCase):

    services = TestCase.services + ["sanitizer"]

    def test_presentation_delete(self):
        """
        Remove element if the last instance of an item is deleted.
        """
        ef = self.element_factory

        klassitem = self.create(ClassItem, UML.Class)
        klass = klassitem.subject

        assert klassitem.subject.presentation[0] is klassitem
        assert klassitem.canvas

        # Delete presentation here:

        klassitem.unlink()

        assert not klassitem.canvas
        assert klass not in self.element_factory.lselect()

    def test_stereotype_attribute_delete(self):
        """
        This test was applicable to the Sanitizer service, but is now resolved
        by a tweak in the data model (Instances diagram).
        """
        factory = self.element_factory
        create = factory.create

        # Set the stage
        # metaklass = create(UML.Class)
        # metaklass.name = 'Class'
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        # ext = UML.model.create_extension(metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        # Now, what happens if the attribute is deleted:
        self.assertTrue(st_attr in stereotype.ownedMember)
        assert slot in instspec.slot

        st_attr.unlink()

        assert [] == list(stereotype.ownedMember)
        assert [] == list(instspec.slot)

    def test_extension_disconnect(self):
        factory = self.element_factory
        create = factory.create

        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = "Class"
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext = UML.model.create_extension(metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        assert stereotype in klass.appliedStereotype[:].classifier

        # Causes set event
        del ext.ownedEnd.type

        assert [] == list(klass.appliedStereotype)

    def test_extension_deletion(self):
        factory = self.element_factory
        create = factory.create

        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = "Class"
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext = UML.model.create_extension(metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        assert stereotype in klass.appliedStereotype[:].classifier

        ext.unlink()

        assert [] == list(klass.appliedStereotype)

    def test_extension_deletion_with_2_metaclasses(self):
        factory = self.element_factory
        create = factory.create

        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = "Class"
        metaiface = create(UML.Class)
        metaiface.name = "Interface"
        klass = create(UML.Class)
        iface = create(UML.Interface)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext1 = UML.model.create_extension(metaklass, stereotype)
        ext2 = UML.model.create_extension(metaiface, stereotype)

        # Apply stereotype to class and create slot
        instspec1 = UML.model.apply_stereotype(klass, stereotype)
        instspec2 = UML.model.apply_stereotype(iface, stereotype)
        slot = UML.model.add_slot(factory, instspec1, st_attr)

        assert stereotype in klass.appliedStereotype[:].classifier
        assert klass in self.element_factory

        ext1.unlink()

        assert [] == list(klass.appliedStereotype)
        assert klass in self.element_factory
        assert [instspec2] == list(iface.appliedStereotype)

    def test_stereotype_deletion(self):
        factory = self.element_factory
        create = factory.create

        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = "Class"
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext = UML.model.create_extension(metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        assert stereotype in klass.appliedStereotype[:].classifier

        stereotype.unlink()

        assert [] == list(klass.appliedStereotype)
