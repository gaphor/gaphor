import pytest

from gaphor import UML
from gaphor.diagram.general import CommentItem
from gaphor.services.copyservice import CopyService


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


@pytest.fixture
def copy_service(event_manager, element_factory, diagrams):
    return CopyService(event_manager, element_factory, diagrams)


def test_copy(copy_service, element_factory):
    diagram = element_factory.create(UML.Diagram)
    ci = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))

    copy_service.copy({ci})
    assert list(diagram.get_all_items()) == [ci]

    copy_service.paste(diagram)

    assert len(list(diagram.get_all_items())) == 2, list(diagram.get_all_items())
