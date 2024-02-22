from gaphor import UML
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.sysml import Block
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
