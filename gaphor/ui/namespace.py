"""
This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
"""

import logging
import operator

# PyGTKCompat used for Gtk.GenericTreeModel Support
import pygtkcompat

pygtkcompat.enable()
pygtkcompat.enable_gtk("3.0")

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

from gaphor import UML
from gaphor.abc import ActionProvider
from gaphor.UML.event import (
    ElementCreateEvent,
    ElementDeleteEvent,
    ModelFactoryEvent,
    FlushFactoryEvent,
    AttributeChangeEvent,
    DerivedSetEvent,
)
from gaphor.core import (
    _,
    event_handler,
    action,
    build_action_group,
    inject,
    transactional,
)
from gaphor.transaction import Transaction
from gaphor.ui.event import DiagramPageChange, DiagramShow
from gaphor.ui import stock
from gaphor.ui.abc import UIComponent
from gaphor.ui.iconoption import get_icon_option

# The following items will be shown in the treeview, although they
# are UML.Namespace elements.
_default_filter_list = (
    UML.Class,
    UML.Interface,
    UML.Package,
    UML.Component,
    UML.Device,
    UML.Node,
    UML.Artifact,
    UML.Interaction,
    UML.UseCase,
    UML.Actor,
    UML.Diagram,
    UML.Profile,
    UML.Stereotype,
    UML.Property,
    UML.Operation,
)


log = logging.getLogger(__name__)


class NamespaceView(Gtk.TreeView):

    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", 0, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", 0, TARGET_STRING),
        Gtk.TargetEntry.new("gaphor/element-id", 0, TARGET_ELEMENT_ID),
    ]

    def __init__(self, model, factory):
        GObject.GObject.__init__(self)
        self.set_model(model)
        self.factory = factory
        self.icon_cache = {}

        self.set_property("headers-visible", False)
        self.set_property("search-column", 0)

        def search_func(model, column, key, iter, data=None):
            assert column == 0
            element = model.get_value(iter, column)
            if element.name:
                return not element.name.startswith(key)

        self.set_search_equal_func(search_func)

        selection = self.get_selection()
        selection.set_mode(Gtk.SelectionMode.BROWSE)
        column = Gtk.TreeViewColumn.new()
        # First cell in the column is for an image...
        cell = Gtk.CellRendererPixbuf()
        column.pack_start(cell, 0)
        column.set_cell_data_func(cell, self._set_pixbuf, None)

        # Second cell if for the name of the object...
        cell = Gtk.CellRendererText()
        # cell.set_property ('editable', 1)
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
        self.connect("drag-begin", NamespaceView.on_drag_begin)
        self.connect("drag-data-get", NamespaceView.on_drag_data_get)
        self.connect("drag-data-delete", NamespaceView.on_drag_data_delete)

        # drop
        self.drag_dest_set(
            Gtk.DestDefaults.ALL, [NamespaceView.DND_TARGETS[-1]], Gdk.DragAction.MOVE
        )
        self.connect("drag-motion", NamespaceView.on_drag_motion)
        self.connect("drag-data-received", NamespaceView.on_drag_data_received)

    def get_selected_element(self):
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return
        return model.get_value(iter, 0)

    def expand_root_nodes(self):
        self.expand_row(path=Gtk.TreePath.new_first(), open_all=False)

    def _set_pixbuf(self, column, cell, model, iter, data):
        value = model.get_value(iter, 0)
        q = t = type(value)

        p = get_icon_option(value)
        if p is not None:
            q = (t, p)

        try:
            icon = self.icon_cache[q]
        except KeyError:
            stock_id = stock.get_stock_id(t, p)
            if stock_id:
                icon = self.render_icon(stock_id, Gtk.IconSize.MENU, "")
            else:
                icon = None
            self.icon_cache[q] = icon
        cell.set_property("pixbuf", icon)

    def _set_text(self, column, cell, model, iter, data):
        """
        Set font and of model elements in tree view.
        """
        value = model.get_value(iter, 0)
        text = value and (value.name or "").replace("\n", " ") or "&lt;None&gt;"

        if isinstance(value, UML.Diagram):
            text = "<b>%s</b>" % text
        elif (
            isinstance(value, UML.Classifier) or isinstance(value, UML.Operation)
        ) and value.isAbstract:
            text = "<i>%s</i>" % text

        cell.set_property("markup", text)

    def _text_edited(self, cell, path_str, new_text):
        """
        The text has been edited. This method updates the data object.
        Note that 'path_str' is a string where the fields are separated by
        colons ':', like this: '0:1:1'. We first turn them into a tuple.
        """
        try:
            model = self.get_property("model")
            iter = model.get_iter_from_string(path_str)
            element = model.get_value(iter, 0)
            tx = Transaction()
            element.name = new_text
            tx.commit()
        except Exception as e:
            log.error('Could not create path from string "%s"' % path_str)

    def on_drag_begin(self, context):
        return True

    def on_drag_data_get(self, context, selection_data, info, time):
        """
        Get the data to be dropped by on_drag_data_received().
        We send the id of the dragged element.
        """
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if iter:
            element = model.get_value(iter, 0)
            p = get_icon_option(element)
            p = p if p else ""
            # 'id#stereotype' is being send
            if info == NamespaceView.TARGET_ELEMENT_ID:
                selection_data.set(
                    selection_data.get_target(), 8, ("%s#%s" % (element.id, p)).encode()
                )
            else:
                selection_data.set(
                    selection_data.get_target(),
                    8,
                    ("%s#%s" % (element.name, p)).encode(),
                )
        return True

    def on_drag_data_delete(self, context):
        """
        Delete data from original site, when `ACTION_MOVE` is used.
        """
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

    def on_drag_data_received(self, context, x, y, selection, info, time):
        """
        Drop the data send by on_drag_data_get().
        """
        self.stop_emission_by_name("drag-data-received")
        if info == NamespaceView.TARGET_ELEMENT_ID:
            n, _p = selection.get_data().decode().split("#")
            drop_info = self.get_dest_row_at_pos(x, y)
        else:
            drop_info = None

        if drop_info:
            model = self.get_model()
            element = self.factory.lookup(n)
            path, position = drop_info
            iter = model.get_iter(path)
            dest_element = model.get_value(iter, 0)
            assert dest_element
            # Add the item to the parent if it is dropped on the same level,
            # else add it to the item.
            if position in (
                Gtk.TreeViewDropPosition.BEFORE,
                Gtk.TreeViewDropPosition.AFTER,
            ):
                parent_iter = model.iter_parent(iter)
                if parent_iter is None:
                    dest_element = None
                else:
                    dest_element = model.get_value(parent_iter, 0)

            try:
                # Check if element is part of the namespace of dest_element:
                ns = dest_element
                while ns:
                    if ns is element:
                        raise AttributeError
                    ns = ns.namespace

                # Set package. This only works for classifiers, packages and
                # diagrams. Properties and operations should not be moved.
                tx = Transaction()
                if dest_element is None:
                    del element.package
                else:
                    element.package = dest_element
                tx.commit()

            except AttributeError as e:
                log.info("Unable to drop data %s" % e)
                context.finish(False, False, time)
            else:
                context.finish(True, True, time)
                # Finally let's try to select the element again.
                # iter = self.iter_for_element(element)
                # if iter:
                #     self.expand_row(
                #         path=Gtk.TreePath.new_from_indices(path[:-1]), open_all=False
                #     )
                # selection = self.get_selection()
                # selection.select_path(path)


class Namespace(UIComponent, ActionProvider):

    title = _("Namespace")
    placement = ("left", "diagrams")

    event_manager = inject("event_manager")
    element_factory = inject("element_factory")
    action_manager = inject("action_manager")

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator />
            <menuitem action="tree-view-create-diagram" />
            <menuitem action="tree-view-create-package" />
            <separator />
            <menuitem action="tree-view-delete-diagram" />
            <menuitem action="tree-view-delete-package" />
            <separator />
          </menu>
        </menubar>
        <popup action="namespace-popup">
          <menuitem action="tree-view-open" />
          <menuitem action="tree-view-rename" />
          <separator />
          <menuitem action="tree-view-create-diagram" />
          <menuitem action="tree-view-create-package" />
          <separator />
          <menuitem action="tree-view-delete-diagram" />
          <menuitem action="tree-view-delete-package" />
        </popup>
      </ui>
    """

    def __init__(self):
        self._namespace = None
        self.action_group = build_action_group(self)
        self.model = Gtk.TreeStore.new([object])
        self.filter = _default_filter_list

    def init(self):
        # Event handler registration is in a separate function,
        # since putting it in with widget construction will cause
        # unit tests to fail, on macOS at least.
        em = self.event_manager
        em.subscribe(self._on_element_create)
        em.subscribe(self._on_element_delete)
        em.subscribe(self._on_model_factory)
        em.subscribe(self._on_flush_factory)
        em.subscribe(self._on_association_set)
        em.subscribe(self._on_attribute_change)

    def open(self):
        self.init()
        return self.construct()

    def close(self):
        if self._namespace:
            self._namespace.destroy()
            self._namespace = None

        em = self.event_manager
        em.unsubscribe(self._on_element_create)
        em.unsubscribe(self._on_element_delete)
        em.unsubscribe(self._on_model_factory)
        em.unsubscribe(self._on_flush_factory)
        em.unsubscribe(self._on_association_set)
        em.unsubscribe(self._on_attribute_change)

    def construct(self):
        sorted_model = Gtk.TreeModelSort(self.model)

        def sort_func(model, iter_a, iter_b, userdata):
            a = (model.get_value(iter_a, 0).name or "").lower()
            b = (model.get_value(iter_b, 0).name or "").lower()
            if a == b:
                return 0
            if a > b:
                return 1
            return -1

        sorted_model.set_sort_func(0, sort_func, None)
        sorted_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        view = NamespaceView(sorted_model, self.element_factory)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.set_placement(Gtk.CornerType.TOP_RIGHT)
        scrolled_window.add(view)
        scrolled_window.show()
        view.show()

        view.connect_after("event-after", self._on_view_event)
        view.connect("row-activated", self._on_view_row_activated)
        view.connect_after("cursor-changed", self._on_view_cursor_changed)
        view.connect("destroy", self._on_view_destroyed)
        self._namespace = view
        self._on_model_factory()

        return scrolled_window

    def iter_for_element(self, element, old_namespace=0):
        # Using `0` as sentinel
        if old_namespace != 0:
            parent_iter = self.iter_for_element(old_namespace)
        elif element and element.namespace:
            parent_iter = self.iter_for_element(element.namespace)
        else:
            parent_iter = None

        child_iter = self.model.iter_children(parent_iter)
        while child_iter:
            if self.model.get_value(child_iter, 0) is element:
                return child_iter
            child_iter = self.model.iter_next(child_iter)
        return None

    def _visible(self, element):
        # Spacial case: Non-navigable properties
        return type(element) in self.filter and not (
            isinstance(element, UML.Property) and element.namespace is None
        )

    @event_handler(ModelFactoryEvent)
    def _on_model_factory(self, event=None):
        """
        Load a new model completely.
        """
        log.info("Rebuilding namespace model")

        def add(element, iter=None):
            if self._visible(element):
                child_iter = self.model.append(iter, [element])
                if isinstance(element, UML.Namespace):
                    for e in element.ownedMember:
                        # check if owned member is indeed within parent's namespace
                        # the check is important in case on Node classes
                        if element is e.namespace:
                            add(e, child_iter)

        self.model.clear()

        toplevel = self.element_factory.select(
            lambda e: type(e) in self.filter and not e.namespace
        )

        for element in toplevel:
            add(element)

        # Expand all root elements:
        if self._namespace:  # None for testing
            self._namespace.expand_root_nodes()
            self._on_view_cursor_changed(self._namespace)

    @event_handler(FlushFactoryEvent)
    def _on_flush_factory(self, event):
        self.model.clear()

    @event_handler(ElementCreateEvent)
    def _on_element_create(self, event):
        element = event.element
        if self._visible(element) and not self.iter_for_element(element):
            iter = self.iter_for_element(element.namespace)
            self.model.append(iter, [element])

    @event_handler(ElementDeleteEvent)
    def _on_element_delete(self, event):
        element = event.element
        if type(element) in self.filter:
            iter = self.iter_for_element(element)
            # iter should be here, unless we try to delete an element who's parent element is already deleted, so let's be lenient.
            if iter:
                self.model.remove(iter)

    @event_handler(DerivedSetEvent)
    def _on_association_set(self, event):

        element = event.element
        if event.property is UML.NamedElement.namespace:
            old_value, new_value = event.old_value, event.new_value

            old_iter = self.iter_for_element(element, old_namespace=old_value)
            if old_iter:
                self.model.remove(old_iter)

            if self._visible(element):
                new_iter = self.iter_for_element(new_value)
                # Should be either set (sub node) or unset (root node)
                if bool(new_iter) == bool(new_value):
                    self.model.append(new_iter, [element])

    @event_handler(AttributeChangeEvent)
    def _on_attribute_change(self, event):
        """
        Element changed, update appropriate row.
        """
        element = event.element

        if (
            event.property is UML.Classifier.isAbstract
            or event.property is UML.BehavioralFeature.isAbstract
            or event.property is UML.NamedElement.name
        ):
            iter = self.iter_for_element(element)
            if iter:
                path = self.model.get_path(iter)
                self.model.row_changed(path, iter)

    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:"
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button.button == 3:
            menu = self.action_manager.get_widget("/namespace-popup")
            menu.popup_at_pointer(event)

    def _on_view_row_activated(self, view, path, column):
        """
        Double click on an element in the tree view.
        """
        self.action_manager.execute("tree-view-open")

    def _on_view_cursor_changed(self, view):
        """
        Another row is selected, toggle action sensitivity.
        """
        element = view.get_selected_element()
        self.action_group.get_action(
            "tree-view-create-diagram"
        ).props.sensitive = isinstance(element, UML.Package)
        self.action_group.get_action(
            "tree-view-create-package"
        ).props.sensitive = isinstance(element, UML.Package)

        self.action_group.get_action(
            "tree-view-delete-diagram"
        ).props.visible = isinstance(element, UML.Diagram)
        self.action_group.get_action("tree-view-delete-package").props.visible = (
            isinstance(element, UML.Package) and not element.presentation
        )

        self.action_group.get_action("tree-view-open").props.sensitive = isinstance(
            element, UML.Diagram
        )

    def _on_view_destroyed(self, widget):
        self.close()

    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = Gtk.TreePath.new_from_indices(
            self._namespace.get_model().path_from_element(element)
        )
        # Expand the first row:
        if len(path.get_indices()) > 1:
            self._namespace.expand_row(path=path, open_all=False)
        selection = self._namespace.get_selection()
        selection.select_path(path)
        self._on_view_cursor_changed(self._namespace)

    @action(name="tree-view-open", label="_Open")
    def tree_view_open_selected(self):
        element = self._namespace.get_selected_element()
        # TODO: Candidate for adapter?
        if isinstance(element, UML.Diagram):
            self.event_manager.handle(DiagramShow(element))

        else:
            log.debug("No action defined for element %s" % type(element).__name__)

    @action(name="tree-view-rename", label=_("Rename"), accel="F2")
    def tree_view_rename_selected(self):
        view = self._namespace
        element = view.get_selected_element()
        if element is not None:
            path = view.get_model().path_from_element(element)
            column = view.get_column(0)
            cell = column.get_cells()[1]
            cell.set_property("editable", 1)
            cell.set_property("text", element.name)
            view.set_cursor(path, column, True)
            cell.set_property("editable", 0)

    @action(
        name="tree-view-create-diagram",
        label=_("_New diagram"),
        stock_id="gaphor-diagram",
    )
    @transactional
    def tree_view_create_diagram(self):
        element = self._namespace.get_selected_element()
        diagram = self.element_factory.create(UML.Diagram)
        diagram.package = element

        if element:
            diagram.name = "%s diagram" % element.name
        else:
            diagram.name = "New diagram"

        self.select_element(diagram)
        self.event_manager.handle(DiagramShow(diagram))
        self.tree_view_rename_selected()

    @action(
        name="tree-view-delete-diagram",
        label=_("_Delete diagram"),
        stock_id="gtk-delete",
    )
    @transactional
    def tree_view_delete_diagram(self):
        diagram = self._namespace.get_selected_element()
        m = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            "Do you really want to delete diagram %s?\n\n"
            "This will possibly delete diagram items\n"
            "that are not shown in other diagrams." % (diagram.name or "<None>"),
        )
        if m.run() == Gtk.ResponseType.YES:
            for i in reversed(diagram.canvas.get_all_items()):
                s = i.subject
                if s and len(s.presentation) == 1:
                    s.unlink()
                i.unlink
            diagram.unlink()
        m.destroy()

    @action(
        name="tree-view-create-package",
        label=_("New _package"),
        stock_id="gaphor-package",
    )
    @transactional
    def tree_view_create_package(self):
        element = self._namespace.get_selected_element()
        package = self.element_factory.create(UML.Package)
        package.package = element

        if element:
            package.name = "%s package" % element.name
        else:
            package.name = "New model"

        self.select_element(package)
        self.tree_view_rename_selected()

    @action(
        name="tree-view-delete-package",
        label=_("Delete pac_kage"),
        stock_id="gtk-delete",
    )
    @transactional
    def tree_view_delete_package(self):
        package = self._namespace.get_selected_element()
        assert isinstance(package, UML.Package)
        package.unlink()
