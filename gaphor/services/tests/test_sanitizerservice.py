
from __future__ import absolute_import
from gaphor.tests import TestCase
from gaphor.UML import uml2, modelfactory
from gaphor.diagram import items


class SanitizerServiceTest(TestCase):

    services = TestCase.services + [ 'sanitizer' ]

    def test_presentation_delete(self):
        """
        Remove element if the last instance of an item is deleted.
        """
        ef = self.element_factory
        
        klassitem = self.create(items.ClassItem, uml2.Class)
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
        #metaklass = create(uml2.Class)
        #metaklass.name = 'Class'
        klass = create(uml2.Class)
        stereotype = create(uml2.Stereotype)
        st_attr = self.element_factory.create(uml2.Property)
        stereotype.ownedAttribute = st_attr
        #ext = modelfactory.create_extension(factory, metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = modelfactory.apply_stereotype(factory, klass, stereotype)
        slot = modelfactory.add_slot(factory, instspec, st_attr)

        # Now, what happens if the attribute is deleted:
        self.assertTrue(st_attr in stereotype.ownedMember)
        self.assertTrue(slot in instspec.slot)

        st_attr.unlink()

        self.assertEquals([], list(stereotype.ownedMember))
        self.assertEquals([], list(instspec.slot))

    def test_extension_disconnect(self):
        factory = self.element_factory
        create = factory.create
        
        # Set the stage
        metaklass = create(uml2.Class)
        metaklass.name = 'Class'
        klass = create(uml2.Class)
        stereotype = create(uml2.Stereotype)
        st_attr = self.element_factory.create(uml2.Property)
        stereotype.ownedAttribute = st_attr
        ext = UML.model.create_extension(factory, metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = UML.model.apply_stereotype(factory, klass, stereotype)
        slot = UML.model.add_slot(factory, instspec, st_attr)

        self.assertTrue(stereotype in klass.appliedStereotype[:].classifier)

        # Causes set event
        del ext.ownedEnd.type

        self.assertEquals([], list(klass.appliedStereotype))

    def test_extension_deletion(self):
        factory = self.element_factory
        create = factory.create
        
        # Set the stage
        metaklass = create(uml2.Class)
        metaklass.name = 'Class'
        klass = create(uml2.Class)
        stereotype = create(uml2.Stereotype)
        st_attr = self.element_factory.create(uml2.Property)
        stereotype.ownedAttribute = st_attr
        ext = UML.model.create_extension(factory, metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = modelfactory.apply_stereotype(factory, klass, stereotype)
        slot = modelfactory.add_slot(factory, instspec, st_attr)

        self.assertTrue(stereotype in klass.appliedStereotype[:].classifier)

        ext.unlink()

        self.assertEquals([], list(klass.appliedStereotype))

    def test_extension_deletion_with_2_metaclasses(self):
        factory = self.element_factory
        create = factory.create
        
        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = 'Class'
        metaiface = create(UML.Class)
        metaiface.name = 'Interface'
        klass = create(UML.Class)
        iface = create(UML.Interface)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext1 = modelfactory.create_extension(factory, metaklass, stereotype)
        ext2 = modelfactory.create_extension(factory, metaiface, stereotype)

        # Apply stereotype to class and create slot
        instspec1 = modelfactory.apply_stereotype(factory, klass, stereotype)
        instspec2 = modelfactory.apply_stereotype(factory, iface, stereotype)
        slot = modelfactory.add_slot(factory, instspec1, st_attr)

        self.assertTrue(stereotype in klass.appliedStereotype[:].classifier)
        self.assertTrue(klass in self.element_factory)

        ext1.unlink()

        self.assertEquals([], list(klass.appliedStereotype))
        self.assertTrue(klass in self.element_factory)
        self.assertEquals([instspec2], list(iface.appliedStereotype))

    def test_stereotype_deletion(self):
        factory = self.element_factory
        create = factory.create
        
        # Set the stage
        metaklass = create(UML.Class)
        metaklass.name = 'Class'
        klass = create(UML.Class)
        stereotype = create(UML.Stereotype)
        st_attr = self.element_factory.create(UML.Property)
        stereotype.ownedAttribute = st_attr
        ext = modelfactory.create_extension(factory, metaklass, stereotype)

        # Apply stereotype to class and create slot
        instspec = modelfactory.apply_stereotype(factory, klass, stereotype)
        slot = modelfactory.add_slot(factory, instspec, st_attr)

        self.assertTrue(stereotype in klass.appliedStereotype[:].classifier)

        stereotype.unlink()

        self.assertEquals([], list(klass.appliedStereotype))

# vim:sw=4:et:ai
