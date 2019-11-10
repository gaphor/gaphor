import pytest

import gaphor.UML as UML
from gaphor.services.eventmanager import EventManager


@pytest.fixture
def factory():
    event_manager = EventManager()
    return UML.ElementFactory(event_manager)


def test_association(factory):
    """Testing Association elements in the meta-model"""
    element = factory.create(UML.Association)

    property1 = factory.create(UML.Property)
    property2 = factory.create(UML.Property)

    element.memberEnd = property1
    element.memberEnd = property2

    element.ownedEnd = property1

    element.navigableOwnedEnd = property1

    assert (
        not element.isDerived
    ), f"The isDerived property should default to False - {element.isDerived}"
    assert (
        property1 in element.member
    ), f"Namespace.member does not contain memberEnd - {element.member}"
    assert (
        property2 in element.member
    ), f"Namespace.member does not contain memberEnd - {element.member}"

    assert (
        property1 in element.feature
    ), f"Classifier.feature does not contain ownedEnd - {element.feature}"
    assert (
        property1 in element.ownedMember
    ), f"Namespace.ownedMember does not contain ownedEnd - {element.ownedEnd}"

    assert property1 in element.ownedEnd, (
        "Association.ownedEnd does not contain navigableOwnedEnd - %s"
        % element.ownedEnd
    )


#    def test_association_class(self):
#        try:
#            element = self.factory.create(UML.AssociationClass)
#        except AttributeError:
#            self.fail('AssociationClass elements are not part of the meta-model')


def test_class(factory):
    """Testing Class elements in the meta-model"""
    element = factory.create(UML.Class)
    property1 = factory.create(UML.Property)
    operation1 = factory.create(UML.Operation)
    element.ownedAttribute = property1
    element.ownedOperation = operation1

    assert (
        property1 in element.attribute
    ), f"Classifier.attribute does not contain ownedAttribute - {element.attribute}"
    assert property1 in element.ownedMember, (
        "Namespace.ownedMember does not contain ownedAttribute - %s"
        % element.ownedMember
    )

    assert (
        operation1 in element.feature
    ), f"Classifier.feature does not contain ownedOperation - {element.feature}"
    assert operation1 in element.ownedMember, (
        "Namespace.ownedMember does not contain ownedOperation" % element.ownedMember
    )


def test_comment(factory):
    """Testing Comment elements in the meta-model"""
    element = factory.create(UML.Comment)
    element.body = "Comment body"
    annotatedElement = factory.create(UML.Class)
    element.annotatedElement = annotatedElement

    assert element.body == "Comment body", f"Incorrect comment body - {element.body}"
    assert (
        annotatedElement in element.annotatedElement
    ), f"Incorrect annotated element - {element.annotatedElement}"


def test_constraint(factory):
    """Testing Constraint elements in the meta-model"""
    element = factory.create(UML.Constraint)

    constrainedElement = factory.create(UML.Class)

    element.constrainedElement = constrainedElement
    element.specification = "Constraint specification"

    assert constrainedElement in element.constrainedElement, (
        "Constraint.constrainedElement does not contain the correct element - %s"
        % element.constrainedElement
    )
    assert (
        element.specification == "Constraint specification"
    ), f"Constraint.specification is incorrect - {element.specification}"


def test_dependency(factory):

    """Testing Dependency elements in the meta-model"""

    element = factory.create(UML.Dependency)

    client = factory.create(UML.Package)
    supplier = factory.create(UML.Package)

    element.client = client
    element.supplier = supplier

    assert (
        client in element.client
    ), f"Dependency.client does not contain client - {element.client}"
    assert (
        supplier in element.supplier
    ), f"Dependency.supplier does not contain supplier - {element.supplier}"


def test_element_import(factory):
    element = factory.create(UML.ElementImport)
    assert element


def test_enumeration(factory):
    element = factory.create(UML.Enumeration)
    assert element


def test_generalization(factory):
    element = factory.create(UML.Generalization)
    assert element


def test_interface(factory):
    element = factory.create(UML.Interface)
    assert element


def test_namespace(factory):
    element = factory.create(UML.Namespace)
    assert element


def test_operation(factory):
    element = factory.create(UML.Operation)
    assert element


def test_package(factory):
    element = factory.create(UML.Package)
    assert element


def test_parameter(factory):
    element = factory.create(UML.Parameter)
    assert element


def test_property(factory):
    element = factory.create(UML.Property)
    assert element


def test_realization(factory):
    element = factory.create(UML.Realization)
    assert element


def test_ids(factory):
    c = factory.create(UML.Class)
    assert c.id
    p = factory.create_as(UML.Class, id=False)
    assert p.id is False, p.id


def test1(factory):
    c = factory.create(UML.Class)
    p = factory.create(UML.Package)
    c.package = p
    assert c.package == p
    assert c.namespace == p
    assert c in p.ownedElement


def testOwnedMember_Unlink(factory):
    c = factory.create(UML.Class)
    p = factory.create(UML.Package)
    c.package = p

    c.unlink()

    assert [p] == factory.lselect()


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


def test_property_is_composite(factory):
    p = UML.Property()
    assert p.isComposite == False, p.isComposite
    p.aggregation = "shared"
    assert p.isComposite == False, p.isComposite
    p.aggregation = "composite"
    assert p.isComposite == True, p.isComposite


def test_association_endType(factory):
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


def test_property_navigability(factory):
    p = factory.create(UML.Property)
    assert p.navigability is None

    c1 = factory.create(UML.Class)
    c2 = factory.create(UML.Class)
    a = UML.model.create_association(c1, c2)
    assert a.memberEnd[0].navigability is None
    assert a.memberEnd[1].navigability is None

    UML.model.set_navigability(a, a.memberEnd[0], True)
    assert a.memberEnd[0].navigability is True
    assert a.memberEnd[1].navigability is None

    UML.model.set_navigability(a, a.memberEnd[0], False)
    assert a.memberEnd[0].navigability is False
    assert a.memberEnd[1].navigability is None


def test_namedelement_qualifiedname(factory):
    p = factory.create(UML.Package)
    p.name = "Package"
    c = factory.create(UML.Class)
    c.name = "Class"

    assert ["Class"] == c.qualifiedName

    p.ownedClassifier = c

    assert ["Package", "Class"] == c.qualifiedName


def test_extension_metaclass(factory):
    c = factory.create(UML.Class)
    c.name = "Class"
    s = factory.create(UML.Stereotype)
    s.name = "Stereotype"

    e = UML.model.create_extension(c, s)

    assert c == e.metaclass


def test_metaclass_extension(factory):
    c = factory.create(UML.Class)
    c.name = "Class"
    s = factory.create(UML.Stereotype)
    s.name = "Stereotype"

    assert [] == c.extension
    assert [] == s.extension

    e = UML.model.create_extension(c, s)

    print(e.memberEnd)
    assert [e] == c.extension
    assert [] == s.extension
    assert e.ownedEnd.type is s


def test_operation_parameter_deletion(factory):
    assert 0 == len(factory.lselect())

    c = factory.create(UML.Class)
    c.name = "Class"
    o = factory.create(UML.Operation)
    c.ownedOperation = o
    UML.parse(o, "a(x: int, y: int)")

    c.unlink()

    assert 0 == len(factory.lselect()), factory.lselect()
