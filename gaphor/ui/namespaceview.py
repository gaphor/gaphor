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


class NamespaceView(Gtk.TreeView):
    if Gtk.get_major_version() == 3:
        TARGET_ELEMENT_ID = 0
        TARGET_GTK_TREE_MODEL_ROW = 1
        DND_TARGETS = [
            Gtk.TargetEntry.new(
                "GTK_TREE_MODEL_ROW",
                Gtk.TargetFlags.SAME_APP,
                TARGET_GTK_TREE_MODEL_ROW,
            ),
            Gtk.TargetEntry.new(
                "gaphor/element-id", Gtk.TargetFlags.SAME_APP, TARGET_ELEMENT_ID
            ),
        ]
    else:
        DND_TARGETS = Gdk.ContentFormats.new(
            ["gaphor/element-id", "GTK_TREE_MODEL_ROW"]
        )

    def __init__(self, model: Gtk.TreeModel):
        Gtk.TreeView.__init__(self)
        self.set_model(model)

        self.set_property("headers-visible", False)
        self.set_property("search-column", 0)

        selection = self.get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        column = Gtk.TreeViewColumn.new()
        # First cell in the column is for an image...
        cell = Gtk.CellRendererPixbuf()
        column.pack_start(cell, 0)
        column.set_cell_data_func(cell, self._set_pixbuf, None)

        # Second cell if for the name of the object...
        cell = Gtk.CellRendererText()
        cell.connect("edited", self._text_edited)
        column.pack_start(cell, 0)
        column.set_cell_data_func(cell, self._set_text, None)

        self.append_column(column)

        if Gtk.get_major_version() == 3:
            self.enable_model_drag_source(
                Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
                NamespaceView.DND_TARGETS,
                Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
            )
            self.enable_model_drag_dest(
                NamespaceView.DND_TARGETS,
                Gdk.DragAction.MOVE,
            )
        else:
            self.enable_model_drag_source(
                Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
                NamespaceView.DND_TARGETS,
                Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
            )
            self.enable_model_drag_dest(
                NamespaceView.DND_TARGETS,
                Gdk.DragAction.MOVE,
            )
        self._controller = tree_view_expand_collapse(self)

    def _set_pixbuf(self, column, cell, model, iter, data):
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

    def _set_text(self, column, cell, model, iter, data):
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
            text = format(element) or "<None>"
        cell.set_property("text", text)

    @transactional
    def _text_edited(self, cell, path_str, new_text):
        """The text has been edited.

        This method updates the data object. Note that 'path_str' is a
        string where the fields are separated by colons ':', like this:
        '0:1:1'. We first turn them into a tuple.
        """
        model = self.get_property("model")
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
