from __future__ import absolute_import
from __future__ import print_function

import unittest

from gaphor.UML import uml2, elementfactory, modelfactory, umllex


class ClassesTestCase(unittest.TestCase):
    def setUp(self):

        self.factory = elementfactory.ElementFactory()

    def tearDown(self):

        del self.factory

    def test_association(self):

        """Testing Association elements in the meta-model"""

        try:

            element = self.factory.create(uml2.Association)

        except AttributeError:

            self.fail('Association elements are not part of the meta-model')

        self.assertFalse(element.isDerived, 'The isDerived property should default to False - %s' % element.isDerived)

        property1 = self.factory.create(uml2.Property)
        property2 = self.factory.create(uml2.Property)

        element.memberEnd = property1
        element.memberEnd = property2

        element.ownedEnd = property1

        element.navigableOwnedEnd = property1

        self.assertTrue(property1 in element.member,
                        'Namespace.member does not contain memberEnd - %s' % element.member)
        self.assertTrue(property2 in element.member,
                        'Namespace.member does not contain memberEnd - %s' % element.member)

        self.assertTrue(property1 in element.feature,
                        'Classifier.feature does not contain ownedEnd - %s' % element.feature)
        self.assertTrue(property1 in element.ownedMember,
                        'Namespace.ownedMember does not contain ownedEnd - %s' % element.ownedEnd)

        self.assertTrue(property1 in element.ownedEnd,
                        'Association.ownedEnd does not contain navigableOwnedEnd - %s' % element.ownedEnd)

    #    def test_association_class(self):
    #        try:
    #            element = self.factory.create(uml2.AssociationClass)
    #        except AttributeError:
    #            self.fail('AssociationClass elements are not part of the meta-model')

    def test_class(self):

        """Testing Class elements in the meta-model"""

        try:

            element = self.factory.create(uml2.Class)

        except AttributeError:

            self.fail('Class elements are not part of the meta-model')

        property1 = self.factory.create(uml2.Property)
        operation1 = self.factory.create(uml2.Operation)

        element.ownedAttribute = property1
        element.ownedOperation = operation1

        self.assertTrue(property1 in element.attribute,
                        'Classifier.attribute does not contain ownedAttribute - %s' % element.attribute)
        self.assertTrue(property1 in element.ownedMember,
                        'Namespace.ownedMember does not contain ownedAttribute - %s' % element.ownedMember)

        self.assertTrue(operation1 in element.feature,
                        'Classifier.feature does not contain ownedOperation - %s' % element.feature)
        self.assertTrue(operation1 in element.ownedMember,
                        'Namespace.ownedMember does not contain ownedOperation' % element.ownedMember)

    def test_comment(self):

        """Testing Comment elements in the meta-model"""

        try:

            element = self.factory.create(uml2.Comment)

        except AttributeError:

            self.fail('Comment elements are not part of the meta-model')

        element.body = 'Comment body'

        self.assertTrue(element.body == 'Comment body', 'Incorrect comment body - %s' % element.body)

        annotatedElement = self.factory.create(uml2.Class)

        element.annotatedElement = annotatedElement

        self.assertTrue(annotatedElement in element.annotatedElement,
                        'Incorrect annotated element - %s' % element.annotatedElement)

    def test_constraint(self):

        """Testing Constraint elements in the meta-model"""

        try:

            element = self.factory.create(uml2.Constraint)

        except AttributeError:

            self.fail('Constraint elements are not part of the meta-model')

        constrainedElement = self.factory.create(uml2.Class)

        element.constrainedElement = constrainedElement
        element.specification = 'Constraint specification'

        self.assertTrue(constrainedElement in element.constrainedElement,
                        'Constraint.constrainedElement does not contain the correct element - %s' % element.constrainedElement)
        self.assertTrue(element.specification == 'Constraint specification',
                        'Constraint.specification is incorrect - %s' % element.specification)

    def test_dependency(self):

        """Testing Dependency elements in the meta-model"""

        try:

            element = self.factory.create(uml2.Dependency)

        except AttributeError:

            self.fail('Dependency elements are not part of the meta-model')

        client = self.factory.create(uml2.Package)
        supplier = self.factory.create(uml2.Package)

        element.client = client
        element.supplier = supplier

        self.assertTrue(client in element.source,
                        'DirectedRelationship.source does not contain client - %s' % element.client)
        self.assertTrue(supplier in element.target,
                        'DirectedRelationship.target does not contain supplier - %s' % element.supplier)

    def test_element_import(self):

        try:

            element = self.factory.create(uml2.ElementImport)

        except AttributeError:

            self.fail('ElementImport elements are not part of the meta-model')

    def test_enumeration(self):

        try:

            element = self.factory.create(uml2.Enumeration)

        except AttributeError:

            self.fail('Enumeration elements are not part of the meta-model')

    def test_generalization(self):

        try:

            element = self.factory.create(uml2.Generalization)

        except AttributeError:

            self.fail('Generalization elements are not part of the meta-model')

    def test_interface(self):

        try:

            element = self.factory.create(uml2.Interface)

        except AttributeError:

            self.fail('Interface elements are not part of the meta-model')

    def test_namespace(self):

        try:

            element = self.factory.create(uml2.Namespace)

        except AttributeError:

            self.fail('Namespace elements are not part of the meta-model')

    def test_operation(self):

        try:

            element = self.factory.create(uml2.Operation)

        except AttributeError:

            self.fail('Operation elements are not part of the meta-model')

    def test_package(self):

        try:

            element = self.factory.create(uml2.Package)

        except AttributeError:

            self.fail('Package elements are not part of the meta-model')

    def test_parameter(self):

        try:

            element = self.factory.create(uml2.Parameter)

        except AttributeError:

            self.fail('Parameter elements are not part of the meta-model')

    def test_property(self):

        try:

            element = self.factory.create(uml2.Property)

        except AttributeError:

            self.fail('Property elements are not part of the meta-model')

    def test_realization(self):

        try:

            element = self.factory.create(uml2.Realization)

        except AttributeError:

            self.fail('Realization elements are not part of the meta-model')


class Uml2TestCase(unittest.TestCase):
    def test_ids(self):
        factory = elementfactory.ElementFactory()
        c = factory.create(uml2.Class)
        assert c.id
        p = factory.create_as(uml2.Class, id=False)
        assert p.id is False, p.id

    def test1(self):
        factory = elementfactory.ElementFactory()
        c = factory.create(uml2.Class)
        p = factory.create(uml2.Package)
        c.package = p
        self.assertEquals(c.package, p)
        self.assertEquals(c.namespace, p)
        self.failUnless(c in p.ownedElement)

    def testOwnedMember_Unlink(self):
        factory = elementfactory.ElementFactory()
        c = factory.create(uml2.Class)
        p = factory.create(uml2.Package)
        c.package = p

        c.unlink()

        self.assertEquals([p], factory.lselect())

    #    def test_lower_upper(self):
    #        """
    #        Test MultiplicityElement.{lower|upper}
    #        """
    #        assert UML.MultiplicityElement.lowerValue in UML.MultiplicityElement.lower.subsets
    #
    #        e = UML.MultiplicityElement()
    #        e.lowerValue = '2'
    #        assert e.lower == '2', e.lower
    #
    #        assert UML.MultiplicityElement.upperValue in UML.MultiplicityElement.upper.subsets
    #
    #        e.upperValue = 'up'
    #        assert UML.MultiplicityElement.upper.version == 4, UML.MultiplicityElement.upper.version
    #        assert e.upper == 'up'
    #        e.upperValue = 'down'
    #        assert UML.MultiplicityElement.upper.version == 5, UML.MultiplicityElement.upper.version
    #        assert e.upper == 'down', e.upper
    #
    #        # TODO: test signal handling

    def test_property_is_composite(self):
        p = uml2.Property()
        assert p.isComposite == False, p.isComposite
        p.aggregation = 'shared'
        assert p.isComposite == False, p.isComposite
        p.aggregation = 'composite'
        assert p.isComposite == True, p.isComposite

    def test_association_endType(self):
        factory = elementfactory.ElementFactory()
        c1 = uml2.Class()
        c2 = uml2.Class()
        a = uml2.Association()
        a.memberEnd = uml2.Property()
        a.memberEnd = uml2.Property()
        a.memberEnd[0].type = c1
        a.memberEnd[1].type = c2
        c1.ownedAttribute = a.memberEnd[0]
        c2.ownedAttribute = a.memberEnd[1]

        assert c1 in a.endType
        assert c2 in a.endType

        c3 = uml2.Class()
        a.memberEnd[1].type = c3

        assert c1 in a.endType
        assert c3 in a.endType

    def test_property_navigability(self):
        factory = elementfactory.ElementFactory()
        p = factory.create(uml2.Property)
        assert p.navigability is None

        c1 = factory.create(uml2.Class)
        c2 = factory.create(uml2.Class)
        a = modelfactory.create_association(factory, c1, c2)
        assert a.memberEnd[0].navigability is None
        assert a.memberEnd[1].navigability is None

        modelfactory.set_navigability(a, a.memberEnd[0], True)
        assert a.memberEnd[0].navigability is True
        assert a.memberEnd[1].navigability is None

        modelfactory.set_navigability(a, a.memberEnd[0], False)
        assert a.memberEnd[0].navigability is False
        assert a.memberEnd[1].navigability is None

    def test_namedelement_qualifiedname(self):
        factory = elementfactory.ElementFactory()
        p = factory.create(uml2.Package)
        p.name = 'Package'
        c = factory.create(uml2.Class)
        c.name = 'Class'

        self.assertEquals(('Class',), c.qualifiedName)

        p.ownedClassifier = c

        self.assertEquals(('Package', 'Class'), c.qualifiedName)

    def test_extension_metaclass(self):
        factory = elementfactory.ElementFactory()
        c = factory.create(uml2.Class)
        c.name = 'Class'
        s = factory.create(uml2.Stereotype)
        s.name = 'Stereotype'

        e = modelfactory.create_extension(factory, c, s)

        self.assertEquals(c, e.metaclass)

    def test_metaclass_extension(self):
        factory = elementfactory.ElementFactory()
        c = factory.create(uml2.Class)
        c.name = 'Class'
        s = factory.create(uml2.Stereotype)
        s.name = 'Stereotype'

        self.assertEquals([], c.extension)
        self.assertEquals([], s.extension)

        e = modelfactory.create_extension(factory, c, s)

        print(e.memberEnd)
        self.assertEquals([e], c.extension)
        self.assertEquals([], s.extension)
        assert e.ownedEnd.type is s

    def test_operation_parameter_deletion(self):
        factory = elementfactory.ElementFactory()
        self.assertEquals(0, len(factory.lselect()))

        c = factory.create(uml2.Class)
        c.name = 'Class'
        o = factory.create(uml2.Operation)
        c.ownedOperation = o
        umllex.parse(o, 'a(x: int, y: int)')

        c.unlink()

        self.assertEquals(0, len(factory.lselect()), factory.lselect())

# vim:sw=4:et:ai
