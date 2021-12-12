from __future__ import annotations

import logging

from gi.repository import Gdk, Gtk, Pango

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.core.format import format, parse
from gaphor.core.modeling import Diagram
from gaphor.diagram.iconname import get_icon_name
from gaphor.ui.namespacemodel import RELATIONSHIPS

log = logging.getLogger(__name__)


def namespace_view(model: Gtk.TreeModel):
    if Gtk.get_major_version() == 3:
        DND_TARGETS = [
            Gtk.TargetEntry.new(
                "GTK_TREE_MODEL_ROW",
                Gtk.TargetFlags.SAME_APP,
                0,
            ),
            Gtk.TargetEntry.new("gaphor/element-id", Gtk.TargetFlags.SAME_APP, 1),
        ]
    else:
        DND_TARGETS = Gdk.ContentFormats.new(
            ["gaphor/element-id", "GTK_TREE_MODEL_ROW"]
        )

    view = Gtk.TreeView.new_with_model(model)

    view.set_property("headers-visible", False)
    view.set_property("search-column", 0)

    selection = view.get_selection()
    selection.set_mode(Gtk.SelectionMode.BROWSE)
    column = Gtk.TreeViewColumn.new()
    column.set_spacing(2)
    # First cell in the column is for an image...
    cell = Gtk.CellRendererPixbuf()
    column.pack_start(cell, 0)
    column.set_cell_data_func(cell, _set_pixbuf, None)

    # Second cell if for the name of the object...
    cell = Gtk.CellRendererText()
    cell.connect("edited", _text_edited, model)
    column.pack_start(cell, 0)
    column.set_cell_data_func(cell, _set_text, None)

    view.append_column(column)

    if Gtk.get_major_version() == 3:
        view.enable_model_drag_source(
            Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
            DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        view.enable_model_drag_dest(
            DND_TARGETS,
            Gdk.DragAction.MOVE,
        )
        view._controller = tree_view_expand_collapse(view)
    else:
        view.enable_model_drag_source(
            Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
            DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        view.enable_model_drag_dest(
            DND_TARGETS,
            Gdk.DragAction.MOVE,
        )
        tree_view_expand_collapse(view)

    def search_func(model, column, key, rowiter):
        # Note that this function returns `False` for a match!
        assert column == 0
        row = model[rowiter]
        not_matched = True

        # Search in child rows.  If any element in the underlying
        # tree matches, it will expand.
        for inner in row.iterchildren():
            if not search_func(model, column, key, inner.iter):
                view.expand_to_path(row.path)
                not_matched = False

        element = list(row)[column]
        if element is not RELATIONSHIPS:
            s = format(element)
            if s and key.lower() in s.lower():
                not_matched = False

        if not_matched:
            view.collapse_row(row.path)

        return not_matched

    view.set_search_equal_func(search_func)

    return view


def _set_pixbuf(column, cell, model, iter, data):
    element = model.get_value(iter, 0)

    if element is RELATIONSHIPS:
        cell.set_property("icon-name", None)
        cell.set_property("visible", False)
    elif isinstance(element, (UML.Property, UML.Operation)):
        cell.set_property("icon-name", None)
        cell.set_property("visible", False)
    else:
        icon_name = get_icon_name(element)
        cell.set_property("visible", True)

        if icon_name:
            cell.set_property("icon-name", icon_name)


def _set_text(column, cell, model, iter, data):
    """Set font and of model elements in tree view."""
    element = model.get_value(iter, 0)

    cell.set_property(
        "weight",
        Pango.Weight.BOLD if isinstance(element, Diagram) else Pango.Weight.NORMAL,
    )

    cell.set_property(
        "style",
        Pango.Style.ITALIC
        if isinstance(element, (UML.Classifier, UML.BehavioralFeature))
        and element.isAbstract
        else Pango.Style.NORMAL,
    )

    if element is RELATIONSHIPS:
        text = gettext("<Relationships>")
    else:
        text = format(element) or gettext("<None>")
    cell.set_property("text", text)


@transactional
def _text_edited(cell, path_str, new_text, model):
    """The text has been edited.

    This method updates the data object. Note that 'path_str' is a
    string where the fields are separated by colons ':', like this:
    '0:1:1'. We first turn them into a tuple.
    """
    iter = model.get_iter_from_string(path_str)
    element = model.get_value(iter, 0)
    try:
        parse(element, new_text)
    except TypeError:
        log.debug(f"No parser for {element}")


def tree_view_expand_collapse(view):
    def on_key_pressed(controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Right:
            path, _column = view.get_cursor()
            view.expand_row(path, state & Gdk.ModifierType.SHIFT_MASK)
            return True
        elif keyval == Gdk.KEY_Left:
            path, _column = view.get_cursor()
            view.collapse_row(path)
            return True

    if Gtk.get_major_version() == 3:
        controller = Gtk.EventControllerKey.new(view)
    else:
        controller = Gtk.EventControllerKey.new()
        view.add_controller(controller)
    controller.connect("key-pressed", on_key_pressed)
    return controller
