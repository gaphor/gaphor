import pytest

from gaphor.UML.actions.activitynodes import ForkNodeItem


class Saver:
    def __call__(self, name, val):
        setattr(self, name, val)


@pytest.fixture
def saver():
    return Saver()


def test_forknode_save_default_height(diagram, saver):
    fork: ForkNodeItem = diagram.create(ForkNodeItem)
    diagram.update({fork})

    fork.save(saver)

    assert saver.height == 30
    assert saver.matrix[5] == 0


def test_forknode_save_height_0(diagram, saver):
    fork: ForkNodeItem = diagram.create(ForkNodeItem)

    fork.handles()[0].pos.y = -100
    fork.handles()[1].pos.y = 0
    diagram.update({fork})

    fork.save(saver)

    assert saver.height == 100
    assert saver.matrix[5] == -100


def test_forknode_save_height_1(diagram, saver):
    fork: ForkNodeItem = diagram.create(ForkNodeItem)

    fork.handles()[0].pos.y = 0
    fork.handles()[1].pos.y = 100
    diagram.update({fork})

    fork.save(saver)

    assert saver.height == 100
    assert saver.matrix[5] == 0
