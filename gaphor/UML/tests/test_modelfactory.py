from __future__ import absolute_import
from gaphor.UML import uml2, modelfactory, elementfactory
from gaphor.UML.modelfactory import STEREOTYPE_FMT as fmt

import unittest

class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.factory = elementfactory.ElementFactory()


class StereotypesTestCase(TestCaseBase):

    def test_stereotype_name(self):
        """Test stereotype name
        """
        stereotype = self.factory.create(uml2.Stereotype)
        stereotype.name = 'Test'
        self.assertEquals('test', modelfactory.stereotype_name(stereotype))

        stereotype.name = 'TEST'
        self.assertEquals('TEST', modelfactory.stereotype_name(stereotype))

        stereotype.name = 'T'
        self.assertEquals('t', modelfactory.stereotype_name(stereotype))

        stereotype.name = ''
        self.assertEquals('', modelfactory.stereotype_name(stereotype))

        stereotype.name = None
        self.assertEquals('', modelfactory.stereotype_name(stereotype))


    def test_stereotypes_conversion(self):
        """Test stereotypes conversion
        """
        s1 = self.factory.create(uml2.Stereotype)
        s2 = self.factory.create(uml2.Stereotype)
        s3 = self.factory.create(uml2.Stereotype)
        s1.name = 's1'
        s2.name = 's2'
        s3.name = 's3'

        cls = self.factory.create(uml2.Class)
        modelfactory.apply_stereotype(self.factory, cls, s1)
        modelfactory.apply_stereotype(self.factory, cls, s2)
        modelfactory.apply_stereotype(self.factory, cls, s3)

        self.assertEquals(fmt % 's1, s2, s3', modelfactory.stereotypes_str(cls))


    def test_no_stereotypes(self):
        """Test stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(uml2.Class)
        self.assertEquals('', modelfactory.stereotypes_str(cls))


    def test_additional_stereotypes(self):
        """Test additional stereotypes conversion
        """
        s1 = self.factory.create(uml2.Stereotype)
        s2 = self.factory.create(uml2.Stereotype)
        s3 = self.factory.create(uml2.Stereotype)
        s1.name = 's1'
        s2.name = 's2'
        s3.name = 's3'

        cls = self.factory.create(uml2.Class)
        modelfactory.apply_stereotype(self.factory, cls, s1)
        modelfactory.apply_stereotype(self.factory, cls, s2)
        modelfactory.apply_stereotype(self.factory, cls, s3)

        result = modelfactory.stereotypes_str(cls, ('test',))
        self.assertEquals(fmt % 'test, s1, s2, s3', result)


    def test_just_additional_stereotypes(self):
        """Test additional stereotypes conversion without applied stereotypes
        """
        cls = self.factory.create(uml2.Class)

        result = modelfactory.stereotypes_str(cls, ('test',))
        self.assertEquals(fmt % 'test', result)


    def test_getting_stereotypes(self):
        """Test getting possible stereotypes
        """
        cls = self.factory.create(uml2.Class)
        cls.name = 'Class'
        st1 = self.factory.create(uml2.Stereotype)
        st1.name = 'st1'
        st2 = self.factory.create(uml2.Stereotype)
        st2.name = 'st2'

        # first extend with st2, to check sorting
        modelfactory.extend_with_stereotype(self.factory, cls, st2)
        modelfactory.extend_with_stereotype(self.factory, cls, st1)

        c1 = self.factory.create(uml2.Class)
        result = tuple(st.name for st in modelfactory.get_stereotypes(self.factory, c1))
        self.assertEquals(('st1', 'st2'), result)


    def test_getting_stereotypes_unique(self):
        """Test if possible stereotypes are unique
        """
        cls1 = self.factory.create(uml2.Class)
        cls1.name = 'Class'
        cls2 = self.factory.create(uml2.Class)
        cls2.name = 'Component'
        st1 = self.factory.create(uml2.Stereotype)
        st1.name = 'st1'
        st2 = self.factory.create(uml2.Stereotype)
        st2.name = 'st2'

        # first extend with st2, to check sorting
        modelfactory.extend_with_stereotype(self.factory, cls1, st2)
        modelfactory.extend_with_stereotype(self.factory, cls1, st1)

        modelfactory.extend_with_stereotype(self.factory, cls2, st1)
        modelfactory.extend_with_stereotype(self.factory, cls2, st2)

        c1 = self.factory.create(uml2.Component)
        result = tuple(st.name for st in modelfactory.get_stereotypes(self.factory, c1))
        self.assertEquals(('st1', 'st2'), result)


    def test_finding_stereotype_instances(self):
        """Test finding stereotype instances
        """
        s1 = self.factory.create(uml2.Stereotype)
        s2 = self.factory.create(uml2.Stereotype)
        s1.name = 's1'
        s2.name = 's2'

        c1 = self.factory.create(uml2.Class)
        c2 = self.factory.create(uml2.Class)
        modelfactory.apply_stereotype(self.factory, c1, s1)
        modelfactory.apply_stereotype(self.factory, c1, s2)
        modelfactory.apply_stereotype(self.factory, c2, s1)

        result = [e.classifier[0].name for e in modelfactory.find_instances(self.factory, s1)]
        self.assertEquals(2, len(result))
        self.assertTrue('s1' in result, result)
        self.assertFalse('s2' in result, result)



class AssociationTestCase(TestCaseBase):
    """
    Association tests.
    """
    def test_creation(self):
        """Test association creation
        """
        c1 = self.factory.create(uml2.Class)
        c2 = self.factory.create(uml2.Class)
        assoc = modelfactory.create_association(self.factory, c1, c2)
        types = [p.type for p in assoc.memberEnd]
        self.assertTrue(c1 in types, assoc.memberEnd)
        self.assertTrue(c2 in types, assoc.memberEnd)

        c1 = self.factory.create(uml2.Interface)
        c2 = self.factory.create(uml2.Interface)
        assoc = modelfactory.create_association(self.factory, c1, c2)
        types = [p.type for p in assoc.memberEnd]
        self.assertTrue(c1 in types, assoc.memberEnd)
        self.assertTrue(c2 in types, assoc.memberEnd)



class AssociationEndNavigabilityTestCase(TestCaseBase):
    """
    Association navigability changes tests.
    """
    def test_attribute_navigability(self):
        """Test navigable attribute of a class or an interface
        """
        c1 = self.factory.create(uml2.Class)
        c2 = self.factory.create(uml2.Class)
        assoc = modelfactory.create_association(self.factory, c1, c2)

        end = assoc.memberEnd[0]
        assert end.type is c1
        assert end.type is c1

        modelfactory.set_navigability(assoc, end, True)

        # class/interface navigablity, Association.navigableOwnedEnd not
        # involved
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end in c2.ownedAttribute)
        self.assertTrue(end.navigability is True)

        # uknown navigability
        modelfactory.set_navigability(assoc, end, None)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end in assoc.ownedEnd)
        self.assertTrue(end not in c2.ownedAttribute)
        self.assertTrue(end.owner is assoc)
        self.assertTrue(end.navigability is None)

        # non-navigability
        modelfactory.set_navigability(assoc, end, False)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end not in c2.ownedAttribute)
        self.assertTrue(end.owner is None)
        self.assertTrue(end.navigability is False)

        # check other navigability change possibilities
        modelfactory.set_navigability(assoc, end, None)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end in assoc.ownedEnd)
        self.assertTrue(end not in c2.ownedAttribute)
        self.assertTrue(end.owner is assoc)
        self.assertTrue(end.navigability is None)

        modelfactory.set_navigability(assoc, end, True)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end in c2.ownedAttribute)
        self.assertTrue(end.owner is c2)
        self.assertTrue(end.navigability is True)


    def test_relationship_navigability(self):
        """Test navigable relationship of a classifier
        """
        n1 = self.factory.create(uml2.Node)
        n2 = self.factory.create(uml2.Node)
        assoc = modelfactory.create_association(self.factory, n1, n2)

        end = assoc.memberEnd[0]
        assert end.type is n1

        modelfactory.set_navigability(assoc, end, True)

        # class/interface navigablity, Association.navigableOwnedEnd not
        # involved
        self.assertTrue(end in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end.navigability is True)

        # uknown navigability
        modelfactory.set_navigability(assoc, end, None)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end in assoc.ownedEnd)
        self.assertTrue(end.navigability is None)

        # non-navigability
        modelfactory.set_navigability(assoc, end, False)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end.navigability is False)

        # check other navigability change possibilities
        modelfactory.set_navigability(assoc, end, None)
        self.assertTrue(end not in assoc.navigableOwnedEnd)
        self.assertTrue(end in assoc.ownedEnd)
        self.assertTrue(end.navigability is None)

        modelfactory.set_navigability(assoc, end, True)
        self.assertTrue(end in assoc.navigableOwnedEnd)
        self.assertTrue(end not in assoc.ownedEnd)
        self.assertTrue(end.navigability is True)



class DependencyTypeTestCase(TestCaseBase):
    """
    Tests for automatic dependency discovery
    """
    def test_usage(self):
        """Test automatic dependency: usage
        """
        cls = self.factory.create(uml2.Class)
        iface = self.factory.create(uml2.Interface)
        dt = modelfactory.dependency_type(cls, iface)
        self.assertEquals(uml2.Usage, dt)


    def test_usage_by_component(self):
        """Test automatic dependency: usage (by component)
        """
        c = self.factory.create(uml2.Component)
        iface = self.factory.create(uml2.Interface)
        dt = modelfactory.dependency_type(c, iface)
        # it should be usage not realization (interface is classifier as
        # well)
        self.assertEquals(uml2.Usage, dt)


    def test_realization(self):
        """Test automatic dependency: realization
        """
        c = self.factory.create(uml2.Component)
        cls = self.factory.create(uml2.Class)
        dt = modelfactory.dependency_type(c, cls)
        self.assertEquals(uml2.Realization, dt)


class MessageTestCase(TestCaseBase):
    """
    Tests for interaction messages.
    """
    def test_create(self):
        """Test message creation
        """
        m = self.factory.create(uml2.Message)
        send = self.factory.create(uml2.MessageOccurrenceSpecification)
        receive = self.factory.create(uml2.MessageOccurrenceSpecification)
        sl = self.factory.create(uml2.Lifeline)
        rl = self.factory.create(uml2.Lifeline)

        send.covered = sl
        receive.covered = rl

        m.sendEvent = send
        m.receiveEvent = receive

        m1 = modelfactory.create_message(self.factory, m, False)
        m2 = modelfactory.create_message(self.factory, m, True)

        self.assertTrue(m1.sendEvent.covered is sl)
        self.assertTrue(m1.receiveEvent.covered is rl)

        self.assertTrue(m2.sendEvent.covered is rl)
        self.assertTrue(m2.receiveEvent.covered is sl)


# vim:sw=4:et
