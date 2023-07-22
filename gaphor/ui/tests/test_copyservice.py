import pytest

from gaphor import UML
from gaphor.core.modeling import Comment, Diagram
from gaphor.diagram.general import CommentItem
from gaphor.ui.copyservice import CopyService
from gaphor.UML.classes import PackageItem


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


@pytest.fixture
def copy_service(event_manager, element_factory, diagrams, monkeypatch):
    copy_buffer = None

    def set_content(self, content_provider):
        nonlocal copy_buffer
        copy_buffer = content_provider.get_value()

    def read_value_async(self, gtype, io_priority, cancellable, callback):
        callback(None, None)

    def read_value_finish(self, res):
        return copy_buffer

    monkeypatch.setattr("gi.repository.Gdk.ContentProvider.new_for_value", lambda v: v)
    monkeypatch.setattr("gi.repository.Gdk.Clipboard.set_content", set_content)
    monkeypatch.setattr(
        "gi.repository.Gdk.Clipboard.read_value_async", read_value_async
    )
    monkeypatch.setattr(
        "gi.repository.Gdk.Clipboard.read_value_finish", read_value_finish
    )

    return CopyService(event_manager, element_factory, diagrams)


def test_copy_link(copy_service, element_factory):
    diagram = element_factory.create(Diagram)
    ci = diagram.create(CommentItem, subject=element_factory.create(Comment))

    copy_service.copy({ci})
    assert list(diagram.get_all_items()) == [ci]

    copy_service.paste_link(diagram)

    assert len(list(diagram.get_all_items())) == 2, list(diagram.get_all_items())


def test_copy_full_with_owned_element(copy_service, element_factory):
    diagram = element_factory.create(Diagram)
    package_item = diagram.create(
        PackageItem, subject=element_factory.create(UML.Package)
    )
    package_item.subject.nestedPackage = element_factory.create(UML.Package)

    copy_service.copy({package_item})

    copy_service.paste_full(diagram)

    assert len(element_factory.lselect(UML.Package)) == 4
