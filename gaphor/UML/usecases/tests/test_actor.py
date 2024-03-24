from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.general import CommentLineItem
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.usecases.actor import ActorItem


def test_create_actor(create, diagram):
    actor_item = create(ActorItem, UML.Actor)
    actor_item.subject.name = "Actor"

    diagram.update({actor_item})


def test_connect_to_lower_port(create, diagram):
    actor_item = create(ActorItem, UML.Actor)
    actor_item.subject.name = "Actor Name"
    line_item = create(CommentLineItem)
    line_head, line_tail = line_item.handles()
    line_head.pos = (50, 100)
    line_tail.pos = (50, 100)

    diagram.update({actor_item, line_item})

    connect(line_item, line_head, actor_item)

    cinfo = diagram.connections.get_connection(line_head)
    assert cinfo.port is actor_item.ports()[-1]


def test_save_and_load(create, diagram, element_factory, saver, loader):
    actor_item = create(ActorItem, UML.Actor)
    actor_item.subject.name = "Actor Name"
    line_item = create(CommentLineItem)
    line_head, line_tail = line_item.handles()
    line_head.pos = (50, 100)
    line_tail.pos = (50, 100)

    diagram.update({actor_item, line_item})

    connect(line_item, line_head, actor_item)

    diagram.update({actor_item, line_item})

    data = saver()
    loader(data)

    new_diagram = next(element_factory.select(Diagram))
    new_actor_item = next(element_factory.select(ActorItem))
    new_line_item = next(element_factory.select(CommentLineItem))
    cinfo = new_diagram.connections.get_connection(new_line_item.head)

    assert cinfo.port is new_actor_item.ports()[-1]
