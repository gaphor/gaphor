
import unittest

import gaphor.UML as UML

class Uml2TestCase(unittest.TestCase):

    def test_ids(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        assert c.id
        p = factory.create_as(UML.Class, id=False)
        assert p.id is False, p.id


    def test1(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        c.package = p
        self.assertEquals(c.package, p)
        self.assertEquals(c.namespace, p)
        self.failUnless(c in p.ownedElement)
        
    def testOwnedMember_Unlink(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        c.package = p

        c.unlink()

        self.assertEquals([p], factory.lselect())


    def test_lower_upper(self):
        """
        Test MultiplicityElement.{lower|upper}
        """
        assert UML.MultiplicityElement.lowerValue in UML.MultiplicityElement.lower.subsets
        assert UML.LiteralSpecification.value in UML.MultiplicityElement.lower.subsets

        e = UML.MultiplicityElement()
        e.lowerValue = UML.LiteralString()
        e.lowerValue.value = '2'
        assert e.lower == '2', e.lower

        assert UML.MultiplicityElement.upperValue in UML.MultiplicityElement.upper.subsets
        assert UML.LiteralSpecification.value in UML.MultiplicityElement.upper.subsets

        e.upperValue = UML.LiteralString()
        e.upperValue.value = 'up'
        assert UML.MultiplicityElement.upper.version == 4, UML.MultiplicityElement.upper.version
        assert e.upper == 'up'
        e.upperValue.value = 'down'
        assert UML.MultiplicityElement.upper.version == 5, UML.MultiplicityElement.upper.version
        assert e.upper == 'down', e.upper

        # TODO: test signal handling

    def test_property_is_composite(self):
        p = UML.Property()
        assert p.isComposite == False, p.isComposite
        p.aggregation = 'shared'
        assert p.isComposite == False, p.isComposite
        p.aggregation = 'composite'
        assert p.isComposite == True, p.isComposite


    def test_association_endType(self):
        factory = UML.ElementFactory()
        c1 = UML.Class()
        c2 = UML.Class()
        a = UML.Association()
        a.memberEnd = UML.Property()
        a.memberEnd = UML.Property()
        a.memberEnd[0].type = c1
        a.memberEnd[1].type = c2
        c1.ownedAttribute = a.memberEnd[0]
        c2.ownedAttribute = a.memberEnd[1]

        assert c1 in a.endType
        assert c2 in a.endType

        c3 = UML.Class()
        a.memberEnd[1].type = c3

        assert c1 in a.endType
        assert c3 in a.endType



    def test_property_navigability(self):
        factory = UML.ElementFactory()
        p = factory.create(UML.Property)
        assert p.navigability is None

        c1 = factory.create(UML.Class)
        c2 = factory.create(UML.Class)
        a = UML.model.create_association(factory, c1, c2)
        assert a.memberEnd[0].navigability is None
        assert a.memberEnd[1].navigability is None

        UML.model.set_navigability(a, a.memberEnd[0], True)
        assert a.memberEnd[0].navigability is True
        assert a.memberEnd[1].navigability is None

        UML.model.set_navigability(a, a.memberEnd[0], False)
        assert a.memberEnd[0].navigability is False
        assert a.memberEnd[1].navigability is None

    def test_namedelement_qualifiedname(self):
        factory = UML.ElementFactory()
        p = factory.create(UML.Package)
        p.name = 'Package'
        c = factory.create(UML.Class)
        c.name = 'Class'

        self.assertEquals(('Class',), c.qualifiedName)

        p.ownedClassifier = c

        self.assertEquals(('Package', 'Class'), c.qualifiedName)


    def test_extension_metaclass(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        c.name = 'Class'
        s = factory.create(UML.Stereotype)
        s.name = 'Stereotype'

        e = UML.model.create_extension(factory, c, s)

        self.assertEquals(c, e.metaclass)

    def test_metaclass_extension(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        c.name = 'Class'
        s = factory.create(UML.Stereotype)
        s.name = 'Stereotype'

        self.assertEquals([], c.extension)
        self.assertEquals([], s.extension)

        e = UML.model.create_extension(factory, c, s)

        print e.memberEnd
        self.assertEquals([e], c.extension)
        self.assertEquals([], s.extension)
        assert e.ownedEnd.type is s

    def test_operation_parameter_deletion(self):
        factory = UML.ElementFactory()
        self.assertEquals(0, len(factory.lselect()))

        c = factory.create(UML.Class)
        c.name = 'Class'
        o = factory.create(UML.Operation)
        c.ownedOperation = o
        UML.parse(o, 'a(x: int, y: int)')

        c.unlink()

        self.assertEquals(0, len(factory.lselect()), factory.lselect())


# vim:sw=4:et:ai
