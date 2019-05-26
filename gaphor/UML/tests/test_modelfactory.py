from gaphor import UML
from gaphor.application import Application
from gaphor.UML.modelfactory import STEREOTYPE_FMT as fmt

import unittest


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.factory = UML.ElementFactory()


class StereotypesTestCase(TestCaseBase):
    def test_stereotype_name(self):
        """Test stereotype name
        """
        stereotype = self.factory.create(UML.Stereotype)
        stereotype.name = "Test"
        assert "test" == UML.model.stereotype_name(stereotype)

        stereotype.name = "TEST"
        assert "TEST" == UML.model.stereotype_name(stereotype)

        stereotype.name = "T"
        assert "t" == UML.model.stereotype_name(stereotype)

        stereotype.name = ""
        assert "" == UML.model.stereotype_name(stereotype)

        stereotype.name = None
        assert "" == UML.model.stereotype_name(stereotype)

    def test_stereotypes_conversion(self):
        """Test stereotypes conversion
        """
        s1 = self.factory.create(UML.Stereotype)
        s2 = self.factory.create(UML.Stereotype)
        s3 = self.factory.create(UML.Stereotype)
        s1.name = "s1"
        s2.name = "s2"
        s3.name = "s3"

        cls = self.factory.create(UML.Class)
        UML.model.apply_stereotype(self.factory, cls, s1)
        UML.model.apply_stereotype(self.factory, cls, s2)
        UML.model.apply_stereotype(self.factory, cls, s3)

        assert (fmt % "s1, s2, s3") == UML.model.stereotypes_str(cls)

    def test_no_stereotypes(self):
        """Test stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(UML.Class)
        assert "" == UML.model.stereotypes_str(cls)

    def test_additional_stereotypes(self):
        """Test additional stereotypes conversion
        """
        s1 = self.factory.create(UML.Stereotype)
        s2 = self.factory.create(UML.Stereotype)
        s3 = self.factory.create(UML.Stereotype)
        s1.name = "s1"
        s2.name = "s2"
        s3.name = "s3"

        cls = self.factory.create(UML.Class)
        UML.model.apply_stereotype(self.factory, cls, s1)
        UML.model.apply_stereotype(self.factory, cls, s2)
        UML.model.apply_stereotype(self.factory, cls, s3)

        result = UML.model.stereotypes_str(cls, ("test",))
        assert (fmt % "test, s1, s2, s3") == result

    def test_just_additional_stereotypes(self):
        """Test additional stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(UML.Class)

        result = UML.model.stereotypes_str(cls, ("test",))
        assert (fmt % "test") == result

    def test_getting_stereotypes(self):
        """Test getting possible stereotypes
        """
        cls = self.factory.create(UML.Class)
        cls.name = "Class"
        st1 = self.factory.create(UML.Stereotype)
        st1.name = "st1"
        st2 = self.factory.create(UML.Stereotype)
        st2.name = "st2"

        # first extend with st2, to check sorting
        UML.model.extend_with_stereotype(self.factory, cls, st2)
        UML.model.extend_with_stereotype(self.factory, cls, st1)

        c1 = self.factory.create(UML.Class)
        result = tuple(st.name for st in UML.model.get_stereotypes(self.factory, c1))
        assert ("st1", "st2") == result

    def test_getting_stereotypes_unique(self):
        """Test if possible stereotypes are unique
        """
        cls1 = self.factory.create(UML.Class)
        cls1.name = "Class"
        cls2 = self.factory.create(UML.Class)
        cls2.name = "Component"
        st1 = self.factory.create(UML.Stereotype)
        st1.name = "st1"
        st2 = self.factory.create(UML.Stereotype)
        st2.name = "st2"

        # first extend with st2, to check sorting
        UML.model.extend_with_stereotype(self.factory, cls1, st2)
        UML.model.extend_with_stereotype(self.factory, cls1, st1)

        UML.model.extend_with_stereotype(self.factory, cls2, st1)
        UML.model.extend_with_stereotype(self.factory, cls2, st2)

        c1 = self.factory.create(UML.Component)
        result = tuple(st.name for st in UML.model.get_stereotypes(self.factory, c1))
        assert ("st1", "st2") == result

    def test_finding_stereotype_instances(self):
        """Test finding stereotype instances
        """
        s1 = self.factory.create(UML.Stereotype)
        s2 = self.factory.create(UML.Stereotype)
        s1.name = "s1"
        s2.name = "s2"

        c1 = self.factory.create(UML.Class)
        c2 = self.factory.create(UML.Class)
        UML.model.apply_stereotype(self.factory, c1, s1)
        UML.model.apply_stereotype(self.factory, c1, s2)
        UML.model.apply_stereotype(self.factory, c2, s1)

        result = [
            e.classifier[0].name for e in UML.model.find_instances(self.factory, s1)
        ]
        assert 2 == len(result)
        assert "s1" in result, result
        assert "s2" not in result, result


class AssociationTestCase(TestCaseBase):
    """
    Association tests.
    """

    def test_creation(self):
        """Test association creation
        """
        c1 = self.factory.create(UML.Class)
        c2 = self.factory.create(UML.Class)
        assoc = UML.model.create_association(self.factory, c1, c2)
        types = [p.type for p in assoc.memberEnd]
        assert c1 in types, assoc.memberEnd
        assert c2 in types, assoc.memberEnd

        c1 = self.factory.create(UML.Interface)
        c2 = self.factory.create(UML.Interface)
        assoc = UML.model.create_association(self.factory, c1, c2)
        types = [p.type for p in assoc.memberEnd]
        assert c1 in types, assoc.memberEnd
        assert c2 in types, assoc.memberEnd


class AssociationEndNavigabilityTestCase(TestCaseBase):
    """
    Association navigability changes tests.
    """

    def test_attribute_navigability(self):
        """Test navigable attribute of a class or an interface
        """
        c1 = self.factory.create(UML.Class)
        c2 = self.factory.create(UML.Class)
        assoc = UML.model.create_association(self.factory, c1, c2)

        end = assoc.memberEnd[0]
        assert end.type is c1
        assert end.type is c1

        UML.model.set_navigability(assoc, end, True)

        # class/interface navigability, Association.navigableOwnedEnd not
        # involved
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        assert end not in assoc.ownedEnd
        assert end in c2.ownedAttribute
        assert end.navigability is True

        # unknown navigability
        UML.model.set_navigability(assoc, end, None)
        assert end not in assoc.navigableOwnedEnd
        assert end in assoc.ownedEnd
        assert end not in c2.ownedAttribute
        assert end.owner is assoc
        assert end.navigability is None

        # non-navigability
        UML.model.set_navigability(assoc, end, False)
        assert end not in assoc.navigableOwnedEnd
        assert end not in assoc.ownedEnd
        assert end not in c2.ownedAttribute
        assert end.owner is None
        assert end.navigability is False

        # check other navigability change possibilities
        UML.model.set_navigability(assoc, end, None)
        assert end not in assoc.navigableOwnedEnd
        assert end in assoc.ownedEnd
        assert end not in c2.ownedAttribute
        assert end.owner is assoc
        assert end.navigability is None

        UML.model.set_navigability(assoc, end, True)
        assert end not in assoc.navigableOwnedEnd
        assert end not in assoc.ownedEnd
        assert end in c2.ownedAttribute
        assert end.owner is c2
        assert end.navigability is True

    def test_relationship_navigability(self):
        """Test navigable relationship of a classifier
        """
        n1 = self.factory.create(UML.Node)
        n2 = self.factory.create(UML.Node)
        assoc = UML.model.create_association(self.factory, n1, n2)

        end = assoc.memberEnd[0]
        assert end.type is n1

        UML.model.set_navigability(assoc, end, True)

        # class/interface navigability, Association.navigableOwnedEnd not
        # involved
        self.assertTrue(end in assoc.navigableOwnedEnd)
        assert end not in assoc.ownedEnd
        assert end.navigability is True

        # unknown navigability
        UML.model.set_navigability(assoc, end, None)
        assert end not in assoc.navigableOwnedEnd
        assert end in assoc.ownedEnd
        assert end.navigability is None

        # non-navigability
        UML.model.set_navigability(assoc, end, False)
        assert end not in assoc.navigableOwnedEnd
        assert end not in assoc.ownedEnd
        assert end.navigability is False

        # check other navigability change possibilities
        UML.model.set_navigability(assoc, end, None)
        assert end not in assoc.navigableOwnedEnd
        assert end in assoc.ownedEnd
        assert end.navigability is None

        UML.model.set_navigability(assoc, end, True)
        assert end in assoc.navigableOwnedEnd
        assert end not in assoc.ownedEnd
        assert end.navigability is True


class DependencyTypeTestCase(TestCaseBase):
    """
    Tests for automatic dependency discovery
    """

    def test_usage(self):
        """Test automatic dependency: usage
        """
        cls = self.factory.create(UML.Class)
        iface = self.factory.create(UML.Interface)
        dt = UML.model.dependency_type(cls, iface)
        assert UML.Usage == dt

    def test_usage_by_component(self):
        """Test automatic dependency: usage (by component)
        """
        c = self.factory.create(UML.Component)
        iface = self.factory.create(UML.Interface)
        dt = UML.model.dependency_type(c, iface)
        # it should be usage not realization (interface is classifier as
        # well)
        self.assertEqual(UML.Usage, dt)

    def test_realization(self):
        """Test automatic dependency: realization
        """
        c = self.factory.create(UML.Component)
        cls = self.factory.create(UML.Class)
        dt = UML.model.dependency_type(c, cls)
        assert UML.Realization == dt


class MessageTestCase(TestCaseBase):
    """
    Tests for interaction messages.
    """

    def test_create(self):
        """Test message creation
        """
        m = self.factory.create(UML.Message)
        send = self.factory.create(UML.MessageOccurrenceSpecification)
        receive = self.factory.create(UML.MessageOccurrenceSpecification)
        sl = self.factory.create(UML.Lifeline)
        rl = self.factory.create(UML.Lifeline)

        send.covered = sl
        receive.covered = rl

        m.sendEvent = send
        m.receiveEvent = receive

        m1 = UML.model.create_message(self.factory, m, False)
        m2 = UML.model.create_message(self.factory, m, True)

        assert m1.sendEvent.covered is sl
        assert m1.receiveEvent.covered is rl

        assert m2.sendEvent.covered is rl
        assert m2.receiveEvent.covered is sl


# vim:sw=4:et
