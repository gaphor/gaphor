from gaphas.selection import Selection

from gaphor import UML
from gaphor.diagram.tools.shortcut import delete_selected_items
from gaphor.UML.diagramitems import PackageItem


class MockView:
    def __init__(self):
        self.selection = Selection()


def test_delete_selected_items(create, diagram, event_manager):
    package_item = create(PackageItem, UML.Package)
    view = MockView()
    view.selection.select_items(package_item)

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation


def test_delete_selected_owner(create, diagram, event_manager):
    package_item = create(PackageItem, UML.Package)
    diagram.element = package_item.subject
    view = MockView()
    view.selection.select_items(package_item)

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation
    assert diagram.element is None
