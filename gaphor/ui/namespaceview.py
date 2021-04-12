from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from gi.repository import Gdk, Gtk, Pango

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.core.format import format, parse
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.iconname import get_icon_name
from gaphor.ui.namespacemodel import RELATIONSHIPS, relationship_iter_parent

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from gaphor.core.modeling import ElementFactory


class NamespaceView(Gtk.TreeView):
    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", 0, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", 0, TARGET_STRING),
        Gtk.TargetEntry.new("gaphor/element-id", 0, TARGET_ELEMENT_ID),
    ]

    def __init__(self, model: Gtk.TreeModel, element_factory: ElementFactory):
        Gtk.TreeView.__init__(self)
        self.set_model(model)
        self.element_factory = element_factory

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

        # drag
        self.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK | Gdk.ModifierType.BUTTON3_MASK,
            NamespaceView.DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        self.connect("drag-data-get", NamespaceView.on_drag_data_get)
        self.connect("drag-data-delete", NamespaceView.on_drag_data_delete)

        # drop
        self.drag_dest_set(
            Gtk.DestDefaults.ALL, [NamespaceView.DND_TARGETS[-1]], Gdk.DragAction.MOVE
        )
        self.connect("drag-motion", NamespaceView.on_drag_motion)
        self.connect("drag-data-received", NamespaceView.on_drag_data_received)

    def get_selected_element(self) -> Optional[Element]:
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return None
        return model.get_value(iter, 0)  # type: ignore[no-any-return]

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

    def on_drag_data_get(self, context, selection_data, info, time):
        """Get the data to be dropped by on_drag_data_received().

        We send the id of the dragged element.
        """
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if iter:
            element = model.get_value(iter, 0)
            if info == NamespaceView.TARGET_ELEMENT_ID:
                selection_data.set(
                    selection_data.get_target(), 8, str(element.id).encode()
                )
            else:
                selection_data.set(
                    selection_data.get_target(), 8, str(element.name).encode()
                )
        return True

    def on_drag_data_delete(self, context):
        """Delete data from original site, when `ACTION_MOVE` is used."""
        self.emit_stop_by_name("drag-data-delete")

    # Drop
    def on_drag_motion(self, context, x, y, time):
        path_pos_or_none = self.get_dest_row_at_pos(x, y)
        if path_pos_or_none:
            self.set_drag_dest_row(*path_pos_or_none)
        else:
            self.set_drag_dest_row(
                Gtk.TreePath.new_from_indices([len(self.get_model()) - 1]),
                Gtk.TreeViewDropPosition.AFTER,
            )
        return True

    @transactional
    def on_drag_data_received(self, context, x, y, selection, info, time):
        """Drop the data send by on_drag_data_get()."""
        self.stop_emission_by_name("drag-data-received")
        if info == NamespaceView.TARGET_ELEMENT_ID:
            element_id = selection.get_data().decode()
            drop_info = self.get_dest_row_at_pos(x, y)
        else:
            drop_info = None

        if drop_info:
            model = self.get_model()
            element = self.element_factory.lookup(element_id)
            if not isinstance(element, (Diagram, UML.Package, UML.Type)):
                log.debug("Element {element} can not be dropped")
                return context.finish(False, False, time)
            path, position = drop_info
            iter = model.get_iter(path)
            dest_element = model.get_value(iter, 0)
            assert dest_element
            if dest_element is RELATIONSHIPS:
                iter = relationship_iter_parent(model, iter)
                dest_element = model.get_value(iter, 0)

            # Add the item to the parent if it is dropped on the same level,
            # else add it to the item.
            if position in (
                Gtk.TreeViewDropPosition.BEFORE,
                Gtk.TreeViewDropPosition.AFTER,
            ):
                parent_iter = model.iter_parent(iter)
                dest_element = (
                    None if parent_iter is None else model.get_value(parent_iter, 0)
                )
            try:
                # Check if element is part of the namespace of dest_element:
                ns = dest_element
                while ns:
                    if ns is element:
                        raise AttributeError
                    ns = ns.namespace

                # Set package. This only works for classifiers, packages and
                # diagrams. Properties and operations should not be moved.
                if dest_element is None:
                    del element.package
                else:
                    element.package = dest_element

            except AttributeError as e:
                log.info(f"Unable to drop data {e}")
                context.finish(False, False, time)
            else:
                context.finish(True, True, time)
