from gaphor.diagram.group import group
from gaphor.UML.uml import Interaction, Lifeline


def test_lifeline_group(element_factory):
    lifeline = element_factory.create(Lifeline)
    interaction = element_factory.create(Interaction)

    assert group(interaction, lifeline)
