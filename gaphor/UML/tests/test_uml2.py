import unittest

import gaphor.UML as UML


class ClassesTestCase(unittest.TestCase):
    def setUp(self):

        self.factory = UML.ElementFactory()

    def tearDown(self):

        del self.factory

    def test_association(self):

        """Testing Association elements in the meta-model"""

        try:

            element = self.factory.create(UML.Association)

        except AttributeError:

            self.fail("Association elements are not part of the meta-model")

        self.assertFalse(
            element.isDerived,
            "The isDerived property should default to False - %s" % element.isDerived,
        )

        property1 = self.factory.create(UML.Property)
        property2 = self.factory.create(UML.Property)

        element.memberEnd = property1
        element.memberEnd = property2

        element.ownedEnd = property1

        element.navigableOwnedEnd = property1

        self.assertTrue(
            property1 in element.member,
            "Namespace.member does not contain memberEnd - %s" % element.member,
        )
        self.assertTrue(
            property2 in element.member,
            "Namespace.member does not contain memberEnd - %s" % element.member,
        )

        self.assertTrue(
            property1 in element.feature,
            "Classifier.feature does not contain ownedEnd - %s" % element.feature,
        )
        self.assertTrue(
            property1 in element.ownedMember,
            "Namespace.ownedMember does not contain ownedEnd - %s" % element.ownedEnd,
        )

        self.assertTrue(
            property1 in element.ownedEnd,
            "Association.ownedEnd does not contain navigableOwnedEnd - %s"
            % element.ownedEnd,
        )

    #    def test_association_class(self):
    #        try:
    #            element = self.factory.create(UML.AssociationClass)
    #        except AttributeError:
    #            self.fail('AssociationClass elements are not part of the meta-model')

    def test_class(self):

        """Testing Class elements in the meta-model"""

        try:

            element = self.factory.create(UML.Class)

        except AttributeError:

            self.fail("Class elements are not part of the meta-model")

        property1 = self.factory.create(UML.Property)
        operation1 = self.factory.create(UML.Operation)

        element.ownedAttribute = property1
        element.ownedOperation = operation1

        self.assertTrue(
            property1 in element.attribute,
            "Classifier.attribute does not contain ownedAttribute - %s"
            % element.attribute,
        )
        self.assertTrue(
            property1 in element.ownedMember,
            "Namespace.ownedMember does not contain ownedAttribute - %s"
            % element.ownedMember,
        )

        self.assertTrue(
            operation1 in element.feature,
            "Classifier.feature does not contain ownedOperation - %s" % element.feature,
        )
        self.assertTrue(
            operation1 in element.ownedMember,
            "Namespace.ownedMember does not contain ownedOperation"
            % element.ownedMember,
        )

    def test_comment(self):

        """Testing Comment elements in the meta-model"""

        try:

            element = self.factory.create(UML.Comment)

        except AttributeError:

            self.fail("Comment elements are not part of the meta-model")

        element.body = "Comment body"

        self.assertTrue(
            element.body == "Comment body", "Incorrect comment body - %s" % element.body
        )

        annotatedElement = self.factory.create(UML.Class)

        element.annotatedElement = annotatedElement

        self.assertTrue(
            annotatedElement in element.annotatedElement,
            "Incorrect annotated element - %s" % element.annotatedElement,
        )

    def test_constraint(self):

        """Testing Constraint elements in the meta-model"""

        try:

            element = self.factory.create(UML.Constraint)

        except AttributeError:

            self.fail("Constraint elements are not part of the meta-model")

        constrainedElement = self.factory.create(UML.Class)

        element.constrainedElement = constrainedElement
        element.specification = "Constraint specification"

        self.assertTrue(
            constrainedElement in element.constrainedElement,
            "Constraint.constrainedElement does not contain the correct element - %s"
            % element.constrainedElement,
        )
        self.assertTrue(
            element.specification == "Constraint specification",
            "Constraint.specification is incorrect - %s" % element.specification,
        )

    def test_dependency(self):

        """Testing Dependency elements in the meta-model"""

        try:

            element = self.factory.create(UML.Dependency)

        except AttributeError:

            self.fail("Dependency elements are not part of the meta-model")

        client = self.factory.create(UML.Package)
        supplier = self.factory.create(UML.Package)

        element.client = client
        element.supplier = supplier

        self.assertTrue(
            client in element.client,
            "Dependency.client does not contain client - %s" % element.client,
        )
        self.assertTrue(
            supplier in element.supplier,
            "Dependency.supplier does not contain supplier - %s" % element.supplier,
        )

    def test_element_import(self):

        try:

            element = self.factory.create(UML.ElementImport)

        except AttributeError:

            self.fail("ElementImport elements are not part of the meta-model")

    def test_enumeration(self):

        try:

            element = self.factory.create(UML.Enumeration)

        except AttributeError:

            self.fail("Enumeration elements are not part of the meta-model")

    def test_generalization(self):

        try:

            element = self.factory.create(UML.Generalization)

        except AttributeError:

            self.fail("Generalization elements are not part of the meta-model")

    def test_interface(self):

        try:

            element = self.factory.create(UML.Interface)

        except AttributeError:

            self.fail("Interface elements are not part of the meta-model")

    def test_namespace(self):

        try:

            element = self.factory.create(UML.Namespace)

        except AttributeError:

            self.fail("Namespace elements are not part of the meta-model")

    def test_operation(self):

        try:

            element = self.factory.create(UML.Operation)

        except AttributeError:

            self.fail("Operation elements are not part of the meta-model")

    def test_package(self):

        try:

            element = self.factory.create(UML.Package)

        except AttributeError:

            self.fail("Package elements are not part of the meta-model")

    def test_parameter(self):

        try:

            element = self.factory.create(UML.Parameter)

        except AttributeError:

            self.fail("Parameter elements are not part of the meta-model")

    def test_property(self):

        try:

            element = self.factory.create(UML.Property)

        except AttributeError:

            self.fail("Property elements are not part of the meta-model")

    def test_realization(self):

        try:

            element = self.factory.create(UML.Realization)

        except AttributeError:

            self.fail("Realization elements are not part of the meta-model")


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
        self.assertEqual(c.package, p)
        self.assertEqual(c.namespace, p)
        self.assertTrue(c in p.ownedElement)

    def testOwnedMember_Unlink(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        p = factory.create(UML.Package)
        c.package = p

        c.unlink()

        self.assertEqual([p], factory.lselect())

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
        p = UML.Property()
        assert p.isComposite == False, p.isComposite
        p.aggregation = "shared"
        assert p.isComposite == False, p.isComposite
        p.aggregation = "composite"
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
        p.name = "Package"
        c = factory.create(UML.Class)
        c.name = "Class"

        self.assertEqual(("Class",), c.qualifiedName)

        p.ownedClassifier = c

        self.assertEqual(("Package", "Class"), c.qualifiedName)

    def test_extension_metaclass(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        c.name = "Class"
        s = factory.create(UML.Stereotype)
        s.name = "Stereotype"

        e = UML.model.create_extension(factory, c, s)

        self.assertEqual(c, e.metaclass)

    def test_metaclass_extension(self):
        factory = UML.ElementFactory()
        c = factory.create(UML.Class)
        c.name = "Class"
        s = factory.create(UML.Stereotype)
        s.name = "Stereotype"

        self.assertEqual([], c.extension)
        self.assertEqual([], s.extension)

        e = UML.model.create_extension(factory, c, s)

        print(e.memberEnd)
        self.assertEqual([e], c.extension)
        self.assertEqual([], s.extension)
        assert e.ownedEnd.type is s

    def test_operation_parameter_deletion(self):
        factory = UML.ElementFactory()
        self.assertEqual(0, len(factory.lselect()))

        c = factory.create(UML.Class)
        c.name = "Class"
        o = factory.create(UML.Operation)
        c.ownedOperation = o
        UML.parse(o, "a(x: int, y: int)")

        c.unlink()

        self.assertEqual(0, len(factory.lselect()), factory.lselect())
