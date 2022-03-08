from gaphor.diagram.group import group, ungroup
from gaphor.SysML.sysml import Block, Property


def test_group(element_factory):
    property = element_factory.create(Property)
    block = element_factory.create(Block)

    assert group(block, property)

    assert property.owner is block


def test_ungroup(element_factory):
    property = element_factory.create(Property)
    block = element_factory.create(Block)
    group(block, property)

    assert ungroup(block, property)

    assert property.owner is None


def test_do_not_ungroup_wrong_parent(element_factory):
    property = element_factory.create(Property)
    block = element_factory.create(Block)
    wrong_block = element_factory.create(Block)
    group(block, property)

    assert not ungroup(wrong_block, property)

    assert property.owner is block
