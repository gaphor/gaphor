from gaphor import UML
from gaphor.diagram.drop import drop
from gaphor.UML.interactions import LifelineItem


def test_drop_class_on_lifeline(element_factory, create, diagram):
    lifeline_item = create(LifelineItem, UML.Lifeline)
    interface = element_factory.create(UML.Interface)

    drop(interface, diagram, 10, 10)

    assert lifeline_item.subject.represents is interface
