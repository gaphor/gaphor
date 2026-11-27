import pytest

from gaphor import UML
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.interfaceblock import InterfaceBlockItem
from gaphor.SysML.sysml import Block, InterfaceBlock
from gaphor.UML.recipes import apply_stereotype


def test_block_item_show_own_stereotype(create):
    block_item = create(BlockItem, Block)

    assert "block" in block_stereotype_text(block_item)


def test_block_item_with_stereotype(element_factory, create):
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.name = "MyStereotype"
    block_item = create(BlockItem, Block)
    apply_stereotype(block_item.subject, stereotype)

    assert "block" not in block_stereotype_text(block_item)
    assert "myStereotype" in block_stereotype_text(block_item)


def block_stereotype_text(block_item):
    return block_item.shape.children[0].child.children[0].child.text()


@pytest.mark.parametrize(
    "item_class,element_class,compartment,aggregation",
    [
        (BlockItem, Block, "show_parts", "composite"),
        (InterfaceBlockItem, InterfaceBlock, "show_references", "shared"),
    ],
)
def test_block_item_updates_when_property_or_its_type_is_renamed(
    create, diagram, item_class, element_class, compartment, aggregation
):
    car = create(item_class, element_class)
    setattr(car, compartment, True)
    wheel = create(BlockItem, Block)
    wheel.subject.name = "Wheel"
    part = car.subject.model.create(UML.Property)
    part.aggregation = aggregation
    part.type = wheel.subject
    car.subject.ownedAttribute = part
    diagram.update()
    width = car.width

    wheel.subject.name = "WheelWithAMuchLongerNameThanBefore"
    diagram.update()

    assert car.width > width

    width = car.width
    part.name = "aPartNameThatIsMuchLongerThanTheTypeNameItself"
    diagram.update()

    assert car.width > width
