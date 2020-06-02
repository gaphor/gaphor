from gaphor import UML


def test_stereotype_name(element_factory):
    """Test stereotype name."""
    stereotype = element_factory.create(UML.Stereotype)
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


def test_stereotypes_conversion(element_factory):
    """Test stereotypes conversion."""
    s1 = element_factory.create(UML.Stereotype)
    s2 = element_factory.create(UML.Stereotype)
    s3 = element_factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"
    s3.name = "s3"

    cls = element_factory.create(UML.Class)
    UML.model.apply_stereotype(cls, s1)
    UML.model.apply_stereotype(cls, s2)
    UML.model.apply_stereotype(cls, s3)

    assert ("«s1, s2, s3»") == UML.model.stereotypes_str(cls)


def test_no_stereotypes(element_factory):
    """Test stereotypes conversion without applied stereotypes."""
    cls = element_factory.create(UML.Class)
    assert "" == UML.model.stereotypes_str(cls)


def test_additional_stereotypes(element_factory):
    """Test additional stereotypes conversion."""
    s1 = element_factory.create(UML.Stereotype)
    s2 = element_factory.create(UML.Stereotype)
    s3 = element_factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"
    s3.name = "s3"

    cls = element_factory.create(UML.Class)
    UML.model.apply_stereotype(cls, s1)
    UML.model.apply_stereotype(cls, s2)
    UML.model.apply_stereotype(cls, s3)

    result = UML.model.stereotypes_str(cls, ("test",))
    assert ("«test, s1, s2, s3»") == result


def test_just_additional_stereotypes(element_factory):
    """Test additional stereotypes conversion without applied stereotypes."""
    cls = element_factory.create(UML.Class)

    result = UML.model.stereotypes_str(cls, ("test",))
    assert ("«test»") == result


def test_getting_stereotypes(element_factory):
    """Test getting possible stereotypes."""
    cls = element_factory.create(UML.Class)
    cls.name = "Class"
    st1 = element_factory.create(UML.Stereotype)
    st1.name = "st1"
    st2 = element_factory.create(UML.Stereotype)
    st2.name = "st2"

    # first extend with st2, to check sorting
    UML.model.create_extension(cls, st2)
    UML.model.create_extension(cls, st1)

    c1 = element_factory.create(UML.Class)
    result = tuple(st.name for st in UML.model.get_stereotypes(c1))
    assert ("st1", "st2") == result


def test_getting_stereotypes_unique(element_factory):
    """Test if possible stereotypes are unique."""
    cls1 = element_factory.create(UML.Class)
    cls1.name = "Class"
    cls2 = element_factory.create(UML.Class)
    cls2.name = "Component"
    st1 = element_factory.create(UML.Stereotype)
    st1.name = "st1"
    st2 = element_factory.create(UML.Stereotype)
    st2.name = "st2"

    # first extend with st2, to check sorting
    UML.model.create_extension(cls1, st2)
    UML.model.create_extension(cls1, st1)

    UML.model.create_extension(cls2, st1)
    UML.model.create_extension(cls2, st2)

    c1 = element_factory.create(UML.Component)
    result = tuple(st.name for st in UML.model.get_stereotypes(c1))
    assert ("st1", "st2") == result


def test_finding_stereotype_instances(element_factory):
    """Test finding stereotype instances."""
    s1 = element_factory.create(UML.Stereotype)
    s2 = element_factory.create(UML.Stereotype)
    s1.name = "s1"
    s2.name = "s2"

    c1 = element_factory.create(UML.Class)
    c2 = element_factory.create(UML.Class)
    UML.model.apply_stereotype(c1, s1)
    UML.model.apply_stereotype(c1, s2)
    UML.model.apply_stereotype(c2, s1)

    result = [e.classifier[0].name for e in UML.model.find_instances(s1)]
    assert len(result) == 2
    assert "s1" in result, result
    assert "s2" not in result, result


# Association tests


def test_creation(element_factory):
    """Test association creation."""
    c1 = element_factory.create(UML.Class)
    c2 = element_factory.create(UML.Class)
    assoc = UML.model.create_association(c1, c2)
    types = [p.type for p in assoc.memberEnd]
    assert c1 in types, assoc.memberEnd
    assert c2 in types, assoc.memberEnd

    c1 = element_factory.create(UML.Interface)
    c2 = element_factory.create(UML.Interface)
    assoc = UML.model.create_association(c1, c2)
    types = [p.type for p in assoc.memberEnd]
    assert c1 in types, assoc.memberEnd
    assert c2 in types, assoc.memberEnd


# Association navigability changes tests.


def test_attribute_navigability(element_factory):
    """Test navigable attribute of a class or an interface."""
    c1 = element_factory.create(UML.Class)
    c2 = element_factory.create(UML.Class)
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


def test_relationship_navigability(element_factory):
    """Test navigable relationship of a classifier."""
    n1 = element_factory.create(UML.Node)
    n2 = element_factory.create(UML.Node)
    assoc = UML.model.create_association(n1, n2)

    end = assoc.memberEnd[0]
    assert end.type is n1

    UML.model.set_navigability(assoc, end, True)

    # class/interface navigability, Association.navigableOwnedEnd not
    # involved
    assert end in n2.ownedAttribute
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
    assert end in n2.ownedAttribute
    assert end not in assoc.ownedEnd
    assert end.navigability is True


# Tests for automatic dependency discovery


def test_usage(element_factory):
    """Test automatic dependency: usage."""
    cls = element_factory.create(UML.Class)
    iface = element_factory.create(UML.Interface)
    dt = UML.model.dependency_type(cls, iface)
    assert UML.Usage == dt


def test_usage_by_component(element_factory):
    """Test automatic dependency: usage (by component)."""
    c = element_factory.create(UML.Component)
    iface = element_factory.create(UML.Interface)
    dt = UML.model.dependency_type(c, iface)
    # it should be usage not realization (interface is classifier as
    # well)
    assert UML.Usage == dt


def test_realization(element_factory):
    """Test automatic dependency: realization."""
    c = element_factory.create(UML.Component)
    cls = element_factory.create(UML.Class)
    dt = UML.model.dependency_type(c, cls)
    assert UML.Realization == dt


# Tests for interaction messages.


def test_interaction_messages_cloning(element_factory):
    """Test message creation."""
    m = element_factory.create(UML.Message)
    send = element_factory.create(UML.MessageOccurrenceSpecification)
    receive = element_factory.create(UML.MessageOccurrenceSpecification)
    sl = element_factory.create(UML.Lifeline)
    rl = element_factory.create(UML.Lifeline)

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
