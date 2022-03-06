import pytest
from gi.repository import Gtk

import gaphor.core.eventmanager
from gaphor import UML
from gaphor.core.modeling import ElementFactory
from gaphor.ui.namespacemodel import RELATIONSHIPS, NamespaceModel


@pytest.fixture
def event_manager():
    return gaphor.core.eventmanager.EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def namespace(event_manager, element_factory):
    namespace = NamespaceModel(event_manager, element_factory)
    yield namespace
    namespace.shutdown()


def test_new_model_is_empty(namespace):
    assert namespace.iter_children(None) is None


def test_root_element(namespace, element_factory):
    element_factory.create(UML.Package)

    assert namespace.iter_n_children(None) == 1


def test_should_add_all_named_elements(namespace, element_factory):
    element_factory.create(UML.Action)

    assert namespace.iter_n_children(None) == 1


def test_multiple_root_elements(namespace, element_factory):
    element_factory.create(UML.Package)
    element_factory.create(UML.Package)

    assert namespace.iter_n_children(None) == 2


def dump_model(model):
    def dump(i):
        while i:
            dump(model.iter_children(i))
            i = model.iter_next(i)

    dump(model.iter_children(None))


def test_nested_elements(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    p2 = element_factory.create(UML.Package)
    p2.package = p1

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    child_iter = namespace.iter_children(iter)

    assert p1 is namespace.get_element(iter)
    assert p2 is namespace.get_element(child_iter)


def test_delete_element(namespace, element_factory):
    p1 = element_factory.create(UML.Package)

    p1.unlink()

    assert namespace.iter_n_children(None) == 0


def test_element_should_not_be_added_if_parent_is_not_valid(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    p2 = element_factory.create(UML.Package)

    p1.unlink()

    p2.package = p1

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    assert namespace.iter_n_children(None) == 0
    assert namespace.iter_n_children(iter) == 0


def test_change_element_name(namespace, element_factory):
    # A row-changed event should be emitted to notify the view of the name change.
    p1 = element_factory.create(UML.Package)
    events = []

    def handle_row_changed(*args):
        events.append(args)

    namespace.connect("row-changed", handle_row_changed)

    p1.name = "pack"

    assert len(events) == 1


def test_move_element_with_children(namespace, element_factory):
    pkg = element_factory.create(UML.Package)
    cls = element_factory.create(UML.Class)
    prp = element_factory.create(UML.Property)

    cls.ownedAttribute = prp
    cls.package = pkg

    pkg_iter = namespace.iter_for_element(pkg)
    cls_iter = namespace.iter_for_element(cls)

    assert namespace.iter_n_children(None) == 1
    assert namespace.iter_n_children(pkg_iter) == 1
    assert namespace.iter_n_children(cls_iter) == 1


def test_element_model_ready(namespace, element_factory):

    with element_factory.block_events():
        p1 = element_factory.create(UML.Package)
        p2 = UML.Package(model=element_factory)

        p2.package = p1
    element_factory.model_ready()

    iter = namespace.iter_for_element(p1)
    assert namespace.iter_n_children(None) == 1
    assert namespace.iter_n_children(iter) == 1


def test_element_factory_flush(namespace, element_factory):
    element_factory.create(UML.Package)
    assert namespace.iter_children(None) is not None

    element_factory.flush()

    assert namespace.iter_children(None) is None


def test_relationships_in_separate_node(namespace, element_factory):
    a = element_factory.create(UML.Association)
    iter = namespace.iter_children(None)
    rel_iter = namespace.iter_children(iter)

    assert namespace.get_element(iter) is RELATIONSHIPS
    assert namespace.get_element(rel_iter) is a


def test_relationship__in_non_package_element(namespace, element_factory):
    c = element_factory.create(UML.Class)
    g = element_factory.create(UML.Generalization)
    iter = namespace.iter_for_element(c)

    g.specific = c

    assert g.owner is c
    assert namespace.iter_n_children(None) == 1
    assert namespace.iter_n_children(iter) == 1
    assert namespace.iter_for_element(g)


def test_all_elements_are_draggable(namespace, element_factory):
    assert namespace.do_row_draggable((0,))


class MockSelectionData:
    def __init__(self, target="GTK_TREE_MODEL_ROW"):
        self._target = target
        self.set_data = None

    def get_target(self):
        return self._target

    def set(self, mock_type, mock_format, data):
        self.set_data = (mock_type, mock_format, data)


def test_droppable(namespace, element_factory, mocker):
    element_factory.create(UML.Class).name = "0"
    element_factory.create(UML.Package).name = "1"
    selection_data = MockSelectionData()
    tree_get_row_drag_data = mocker.patch.object(Gtk, "tree_get_row_drag_data")
    tree_get_row_drag_data.return_value = (True, namespace, (0,))

    assert namespace.do_row_drop_possible(
        Gtk.TreePath.new_from_indices((1, 0)), selection_data
    )


@pytest.mark.skipif(Gtk.get_major_version() != 3, reason="Works only for GTK+ 3")
def test_drag_data_get_for_model_row(namespace, element_factory, mocker):
    element_factory.create(UML.Class)
    selection_data = MockSelectionData()
    tree_set_row_drag_data = mocker.patch.object(Gtk, "tree_set_row_drag_data")
    tree_set_row_drag_data.return_value = True

    assert namespace.do_drag_data_get((0,), selection_data)
    tree_set_row_drag_data.assert_called_once()


def test_drag_data_get_element_id(namespace, element_factory):
    c = element_factory.create(UML.Class)
    selection_data = MockSelectionData(target="gaphor/element-id")
    assert namespace.do_drag_data_get((0,), selection_data)
    type, format, data = selection_data.set_data

    assert data == c.id.encode()


def test_drag_data_received(namespace, element_factory, mocker):
    element_factory.create(UML.Class)
    element_factory.create(UML.Package)
    selection_data = MockSelectionData()
    tree_get_row_drag_data = mocker.patch.object(Gtk, "tree_get_row_drag_data")
    tree_get_row_drag_data.return_value = (
        True,
        namespace,
        Gtk.TreePath.new_from_indices((0,)),
    )

    assert namespace.do_drag_data_received(
        Gtk.TreePath.new_from_indices((1,)), selection_data
    )
