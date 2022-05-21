from __future__ import annotations

from gi.repository import Gio, GLib, GObject, Gtk

from gaphor.diagram.iconname import get_icon_name
from gaphor.i18n import gettext, translated_ui_string


class TreeItem(GObject.GObject):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self._text = format(element) or gettext("<None>")
        self._icon = get_icon_name(element)
        self.child_model = None

    @GObject.Property(type=str)
    def text(self):
        return self._text

    @text.setter  # type: ignore[no-redef]
    def text(self, text):
        self._text = text

    @GObject.Property(type=str)
    def icon(self):
        return self._name


class TreeModel(GObject.Object, Gio.ListModel):
    def __init__(self, element_factory, owner):
        super().__init__()
        self.items = [TreeItem(e) for e in element_factory.select() if e.owner is owner]

    def do_get_item_type(self) -> GObject.GType:
        return TreeItem.__gtype__

    def do_get_n_items(self) -> int:
        return len(self.items)

    def do_get_item(self, position) -> GObject.Object | None:
        try:
            return self.items[position]
        except IndexError:
            return None


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "viewitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


def tree_view(element_factory):
    def child_model(item, user_data):
        if not item.child_model:
            item.child_model = TreeModel(element_factory, owner=item.element)
        return item.child_model

    model = TreeModel(element_factory, owner=None)
    tree = Gtk.TreeListModel.new(
        model,
        passthrough=False,
        autoexpand=False,
        create_func=child_model,
        user_data=None,
    )

    selection = Gtk.SingleSelection.new(tree)
    factory = Gtk.BuilderListItemFactory.new_from_bytes(None, new_list_item_ui())

    return Gtk.ListView.new(selection, factory)
