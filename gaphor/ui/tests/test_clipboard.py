import pytest

from gaphor import UML
from gaphor.ui.clipboard import Clipboard
from gaphor.UML.classes import PackageItem
from gaphor.UML.general import CommentItem


class MockSystemClipboard:
    def __init__(self):
        self.copy_buffer = None

    def set_content(self, content_provider):
        self.copy_buffer = content_provider.get_value()

    def read_value_async(self, gtype, io_priority, cancellable, callback):
        callback(None, self.copy_buffer)

    def read_value_finish(self, result):
        return result


@pytest.fixture
def clipboard(event_manager, element_factory, monkeypatch):
    monkeypatch.setattr("gi.repository.Gdk.ContentProvider.new_for_value", lambda v: v)

    return Clipboard(event_manager, element_factory, MockSystemClipboard())


def test_copy_link(clipboard, diagram, view, element_factory):
    ci = diagram.create(CommentItem, subject=element_factory.create(UML.Comment))
    view.selection.select_items(ci)

    clipboard.copy(view)
    assert list(diagram.get_all_items()) == [ci]

    clipboard.paste_link(view)

    assert ci in diagram.get_all_items()
    assert len(list(diagram.get_all_items())) == 2, list(diagram.get_all_items())


def test_copy_full_with_owned_element(clipboard, diagram, view, element_factory):
    package_item = diagram.create(
        PackageItem, subject=element_factory.create(UML.Package)
    )
    package_item.subject.nestedPackage = element_factory.create(UML.Package)
    view.selection.select_items(package_item)

    clipboard.copy(view)

    clipboard.paste_full(view)

    assert len(element_factory.lselect(UML.Package)) == 4
