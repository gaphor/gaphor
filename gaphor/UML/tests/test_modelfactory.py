import pytest

from gaphor import UML
from gaphor.services.eventmanager import EventManager


@pytest.fixture
def factory():
    event_manager = EventManager()
    return UML.ElementFactory(event_manager)


def test_stereotype_name(factory):
    """Test stereotype name."""
    stereotype = factory.create(UML.Stereotype)
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


def test_stereotypes_conversion(factory):
    """Test stereotypes conversion."""
    s1 = factory.create(UML.Stereotype)
    s2 = factory.create(UML.Stereotype)
    s3 = factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"
    s3.name = "s3"

    cls = factory.create(UML.Class)
    UML.model.apply_stereotype(cls, s1)
    UML.model.apply_stereotype(cls, s2)
    UML.model.apply_stereotype(cls, s3)

    assert ("«s1, s2, s3»") == UML.model.stereotypes_str(cls)


def test_no_stereotypes(factory):
    """Test stereotypes conversion without applied stereotypes."""
    cls = factory.create(UML.Class)
    assert "" == UML.model.stereotypes_str(cls)


def test_additional_stereotypes(factory):
    """Test additional stereotypes conversion."""
    s1 = factory.create(UML.Stereotype)
    s2 = factory.create(UML.Stereotype)
    s3 = factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"
    s3.name = "s3"

    cls = factory.create(UML.Class)
    UML.model.apply_stereotype(cls, s1)
    UML.model.apply_stereotype(cls, s2)
    UML.model.apply_stereotype(cls, s3)

    result = UML.model.stereotypes_str(cls, ("test",))
    assert ("«test, s1, s2, s3»") == result


def test_just_additional_stereotypes(factory):
    """Test additional stereotypes conversion without applied stereotypes."""
    cls = factory.create(UML.Class)

    result = UML.model.stereotypes_str(cls, ("test",))
    assert ("«test»") == result


def test_getting_stereotypes(factory):
    """Test getting possible stereotypes."""
    cls = factory.create(UML.Class)
    cls.name = "Class"
    st1 = factory.create(UML.Stereotype)
    st1.name = "st1"
    st2 = factory.create(UML.Stereotype)
    st2.name = "st2"

    # first extend with st2, to check sorting
    UML.model.create_extension(cls, st2)
    UML.model.create_extension(cls, st1)

    c1 = factory.create(UML.Class)
    result = tuple(st.name for st in UML.model.get_stereotypes(c1))
    assert ("st1", "st2") == result


def test_getting_stereotypes_unique(factory):
    """Test if possible stereotypes are unique."""
    cls1 = factory.create(UML.Class)
    cls1.name = "Class"
    cls2 = factory.create(UML.Class)
    cls2.name = "Component"
    st1 = factory.create(UML.Stereotype)
    st1.name = "st1"
    st2 = factory.create(UML.Stereotype)
    st2.name = "st2"

    # first extend with st2, to check sorting
    UML.model.create_extension(cls1, st2)
    UML.model.create_extension(cls1, st1)

    UML.model.create_extension(cls2, st1)
    UML.model.create_extension(cls2, st2)

    c1 = factory.create(UML.Component)
    result = tuple(st.name for st in UML.model.get_stereotypes(c1))
    assert ("st1", "st2") == result


def test_finding_stereotype_instances(factory):
    """Test finding stereotype instances."""
    s1 = factory.create(UML.Stereotype)
    s2 = factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"

    c1 = factory.create(UML.Class)
    c2 = factory.create(UML.Class)
    UML.model.apply_stereotype(c1, s1)
    UML.model.apply_stereotype(c1, s2)
    UML.model.apply_stereotype(c2, s1)

    result = [e.classifier[0].name for e in UML.model.find_instances(s1)]
    assert 2 == len(result)
    assert "s1" in result, result
    assert "s2" not in result, result


# Association tests


def test_creation(factory):
    """Test association creation."""
    c1 = factory.create(UML.Class)
    c2 = factory.create(UML.Class)
    assoc = UML.model.create_association(c1, c2)
    types = [p.type for p in assoc.memberEnd]
    assert c1 in types, assoc.memberEnd
    assert c2 in types, assoc.memberEnd

    c1 = factory.create(UML.Interface)
    c2 = factory.create(UML.Interface)
    assoc = UML.model.create_association(c1, c2)
    types = [p.type for p in assoc.memberEnd]
    assert c1 in types, assoc.memberEnd
    assert c2 in types, assoc.memberEnd


# Association navigability changes tests.


def test_attribute_navigability(factory):
    """Test navigable attribute of a class or an interface."""
    c1 = factory.create(UML.Class)
    c2 = factory.create(UML.Class)
    assoc = UML.model.create_association(c1, c2)

    end = assoc.memberEnd[0]
    assert end.type is c1
    assert end.type is c1

    UML.model.set_navigability(assoc, end, True)

    # class/interface navigability, Association.navigableOwnedEnd not
    # involved
    assert end not in assoc.navigableOwnedEnd
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


def test_relationship_navigability(factory):
    """Test navigable relationship of a classifier."""
    n1 = factory.create(UML.Node)
    n2 = factory.create(UML.Node)
    assoc = UML.model.create_association(n1, n2)

    end = assoc.memberEnd[0]
    assert end.type is n1

    UML.model.set_navigability(assoc, end, True)

    # class/interface navigability, Association.navigableOwnedEnd not
    # involved
    assert end in assoc.navigableOwnedEnd
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


# Tests for automatic dependency discovery


def test_usage(factory):
    """Test automatic dependency: usage."""
    cls = factory.create(UML.Class)
    iface = factory.create(UML.Interface)
    dt = UML.model.dependency_type(cls, iface)
    assert UML.Usage == dt


def test_usage_by_component(factory):
    """Test automatic dependency: usage (by component)."""
    c = factory.create(UML.Component)
    iface = factory.create(UML.Interface)
    dt = UML.model.dependency_type(c, iface)
    # it should be usage not realization (interface is classifier as
    # well)
    assert UML.Usage == dt


def test_realization(factory):
    """Test automatic dependency: realization."""
    c = factory.create(UML.Component)
    cls = factory.create(UML.Class)
    dt = UML.model.dependency_type(c, cls)
    assert UML.Realization == dt


# Tests for interaction messages.


def test_create(factory):
    """Test message creation."""
    m = factory.create(UML.Message)
    send = factory.create(UML.MessageOccurrenceSpecification)
    receive = factory.create(UML.MessageOccurrenceSpecification)
    sl = factory.create(UML.Lifeline)
    rl = factory.create(UML.Lifeline)

    send.covered = sl
    receive.covered = rl

    m.sendEvent = send
    m.receiveEvent = receive

    m1 = UML.model.clone_message(m, False)
    m2 = UML.model.clone_message(m, True)

    assert m1.sendEvent.covered is sl
    assert m1.receiveEvent.covered is rl

    assert m2.sendEvent.covered is rl
    assert m2.receiveEvent.covered is sl
