from gi.repository import Gtk

from gaphor.diagram.connectors import Connector
from gaphor.diagram.copypaste import copy, paste_link
from gaphor.diagram.presentation import connect as _connect


def allow(line, handle, item, port=None) -> bool:
    if port is None and len(item.ports()) > 0:
        port = item.ports()[0]

    adapter = Connector(item, line)
    return adapter.allow(handle, port)


def connect(line, handle, item, port=None):
    """Connect line's handle to an item.

    If port is not provided, then first port is used.
    """
    _connect(line, handle, item)

    cinfo = line.diagram.connections.get_connection(handle)
    assert cinfo.connected is item
    assert cinfo.port


def disconnect(line, handle):
    """Disconnect line's handle."""
    diagram = line.diagram

    diagram.connections.disconnect_item(line, handle)
    assert not diagram.connections.get_connection(handle)


def get_connected(item, handle):
    assert handle in item.handles()
    if cinfo := item.diagram.connections.get_connection(handle):
        return cinfo.connected  # type: ignore[no-any-return] # noqa: F723
    return None


def clear_model(diagram, element_factory, retain=[]):
    """Clear the model and diagram, leaving only an empty diagram."""
    for element in list(element_factory.values()):
        if element is not diagram and element not in retain:
            element.unlink()

    for item in diagram.get_all_items():
        item.unlink()


def copy_and_paste_link(items, diagram, element_factory, retain=[]):
    buffer = copy(items)
    return paste_link(buffer, diagram, element_factory.lookup)


def copy_clear_and_paste_link(items, diagram, element_factory, retain=[]):
    buffer = copy(items)
    clear_model(diagram, element_factory, retain)
    return paste_link(buffer, diagram, element_factory.lookup)


if Gtk.get_major_version() == 3:

    def find(widget, name):
        if Gtk.Buildable.get_name(widget) == name:
            return widget
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                if found := find(child, name):
                    return found
        return None

else:

    def find(widget, name):
        if widget.get_buildable_id() == name:
            return widget
        if sibling := widget.get_next_sibling():
            if found := find(sibling, name):
                return found
        if child := widget.get_first_child():
            if found := find(child, name):
                return found

        return None
