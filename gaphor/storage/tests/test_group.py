import pytest

from gaphor.UML.classes import DependencyItem
from gaphor.UML.components import NodeItem

PARENT_X = 189
PARENT_Y = 207
CHILD_ONE_X = 32
CHILD_ONE_Y = 54
CHILD_TWO_X = 44
CHILD_TWO_Y = 208


def handle_pos(item, handle_index):
    return tuple(map(float, item.handles()[handle_index].pos))


def test_load_grouped_connected_items(element_factory, loader):
    loader(NODE_EXAMPLE_XML)

    diagram = element_factory.lselect()[0]
    canvas = diagram.canvas
    node_item, dep_item = canvas.get_root_items()
    child_one, child_two = canvas.get_children(node_item)

    assert isinstance(node_item, NodeItem)
    assert isinstance(dep_item, DependencyItem)
    assert isinstance(child_one, NodeItem)
    assert isinstance(child_two, NodeItem)

    assert canvas.get_parent(child_one) is node_item

    assert tuple(canvas.get_matrix_i2c(child_one)) == (
        1.0,
        0.0,
        0.0,
        1.0,
        PARENT_X + CHILD_ONE_X,
        PARENT_Y + CHILD_ONE_Y,
    )
    assert tuple(canvas.get_matrix_i2c(child_two)) == (
        1.0,
        0.0,
        0.0,
        1.0,
        PARENT_X + CHILD_TWO_X,
        PARENT_Y + CHILD_TWO_Y,
    )


NODE_EXAMPLE_XML = f"""\
<?xml version="1.0" encoding="utf-8"?>
<gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="1.2.0rc2">
  <Diagram id="3ea414eb-5eb5-11ea-9ccf-45e3771927d8">
    <canvas>
      <item id="41f681ab-5eb5-11ea-9ccf-45e3771927d8" type="NodeItem">
        <matrix>
          <val>(1.0, 0.0, 0.0, 1.0, {PARENT_X}, {PARENT_Y})</val>
        </matrix>
        <width>
          <val>388.5</val>
        </width>
        <height>
          <val>286.5</val>
        </height>
        <item id="4541c555-5eb5-11ea-9ccf-45e3771927d8" type="NodeItem">
          <matrix>
            <val>(1.0, 0.0, 0.0, 1.0, {CHILD_ONE_X}, {CHILD_ONE_Y})</val>
          </matrix>
          <width>
            <val>100.0</val>
          </width>
          <height>
            <val>50.0</val>
          </height>
        </item>
        <item id="4f927913-5eb5-11ea-9ccf-45e3771927d8" type="NodeItem">
          <matrix>
            <val>(1.0, 0.0, 0.0, 1.0, {CHILD_TWO_X}, {CHILD_TWO_Y})</val>
          </matrix>
          <width>
            <val>100.0</val>
          </width>
          <height>
            <val>50.0</val>
          </height>
        </item>
      </item>
      <item id="5b4d81cb-5eb5-11ea-9ccf-45e3771927d8" type="DependencyItem">
        <matrix>
          <val>(1.0, 0.0, 0.0, 1.0, 274.0, 312.0)</val>
        </matrix>
        <points>
          <val>[(0.0, 0.0), (6.0, 104.0)]</val>
        </points>
        <head-connection>
          <ref refid="4541c555-5eb5-11ea-9ccf-45e3771927d8"/>
        </head-connection>
        <tail-connection>
          <ref refid="4f927913-5eb5-11ea-9ccf-45e3771927d8"/>
        </tail-connection>
      </item>
    </canvas>
  </Diagram>
</gaphor>
"""
