from gaphor.diagram.tests.fixtures import connect
from gaphor.UML.classes import AssociationItem, ClassItem
from gaphor.UML.uml import Actor, Class, UseCase
from gaphor.UML.usecases.actor import ActorItem
from gaphor.UML.usecases.usecase import UseCaseItem


def test_connect_usecase_actor(create):
    actor_item = create(ActorItem, element_class=Actor)
    use_case_item = create(UseCaseItem, element_class=UseCase)
    association_item = create(AssociationItem)

    connect(association_item, association_item.head, actor_item)
    connect(association_item, association_item.tail, use_case_item)

    assert association_item.subject
    assert actor_item.subject in association_item.subject.ownedMember[:].type
    assert use_case_item.subject in association_item.subject.ownedMember[:].type


def test_connect_class_actor(create):
    actor_item = create(ActorItem, element_class=Actor)
    class_item = create(ClassItem, element_class=Class)
    association_item = create(AssociationItem)

    connect(association_item, association_item.head, actor_item)
    connect(association_item, association_item.tail, class_item)

    assert association_item.subject
    assert actor_item.subject in association_item.subject.ownedMember[:].type
    assert class_item.subject in association_item.subject.ownedMember[:].type
