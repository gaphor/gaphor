from gaphor import UML
from gaphor.core import Transaction
from gaphor.core.modeling import Diagram
from gaphor.UML.classes import ClassItem


class ViewMock:
    def __init__(self, diagram):
        self.updates = []
        diagram.register_view(self)

    def request_update(self, items=(), removed_items=()):
        self.updates.append((items, removed_items))


def test_undo_should_remove_shown_item_on_diagram(
    event_manager, element_factory, undo_manager
):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    view = ViewMock(diagram)

    with Transaction(event_manager):
        cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    undo_manager.undo_transaction()

    _items, removed_items = view.updates[-1]

    assert cls in removed_items, view.updates


def test_redo_should_show_item_on_diagram(event_manager, element_factory, undo_manager):
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)

    view = ViewMock(diagram)

    with Transaction(event_manager):
        cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    undo_manager.undo_transaction()
    undo_manager.redo_transaction()

    items, _removed_items = view.updates[-1]

    assert cls.id in (item.id for item in items), items
