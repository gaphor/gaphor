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
from zope import component
from zope.interface import implementer

from gaphor import UML
from gaphor.interfaces import IActionProvider
from gaphor.UML.event import (
    ElementCreateEvent,
    ModelFactoryEvent,
    FlushFactoryEvent,
    DerivedSetEvent,
)
from gaphor.UML.interfaces import IAttributeChangeEvent, IElementDeleteEvent
from gaphor.core import _, action, build_action_group, inject, transactional
from gaphor.transaction import Transaction
from gaphor.ui import stock
from gaphor.ui.iconoption import get_icon_option
from gaphor.ui.interfaces import IUIComponent

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

# TODO: update tree sorter:
# Diagram before Class & Package.
# Property before Operation
_name_getter = operator.attrgetter("name")
_tree_sorter = lambda e: _name_getter(e) or ""

log = logging.getLogger(__name__)


def catchall(func):
    def catchall_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            log.error(
                "Exception in %s. Try to refresh the entire model" % (func,),
                exc_info=True,
            )
            try:
                args[0].refresh()
            except Exception as e:
                log.error("Failed to refresh")

    return catchall_wrapper


class NamespaceModel(Gtk.GenericTreeModel):
    """
    The NamespaceModel holds a view on the data model based on namespace
    relationships (such as a Package containing a Class).

    NamedElement.namespace[1] -- Namespace.ownedMember[*]

    NOTE: when a model is loaded no IAssociation*Event's are emitted.

    """

    component_registry = inject("component_registry")

    def __init__(self, factory):
        # Init parent:
        Gtk.GenericTreeModel.__init__(self)

        self.stamp = 0

        #: Dictionary of (id(user_data): user_data), used when leak-references=False
        self._held_refs = {}

        # We own the references to the iterators.
        self.set_property("leak-references", 0)

        self.factory = factory

        self._nodes = {None: []}

        self.filter = _default_filter_list

        cr = self.component_registry
        cr.register_handler(self.flush)
        cr.register_handler(self.refresh)
        cr.register_handler(self._on_element_change)
        cr.register_handler(self._on_element_create)
        cr.register_handler(self._on_element_delete)
        cr.register_handler(self._on_association_set)

        self._build_model()

    def close(self):
        """
        Close the namespace model, unregister handlers.
        """
        cr = self.component_registry
        cr.unregister_handler(self.flush)
        cr.unregister_handler(self.refresh)
        cr.unregister_handler(self._on_element_change)
        cr.unregister_handler(self._on_element_create)
        cr.unregister_handler(self._on_element_delete)
        cr.unregister_handler(self._on_association_set)

    def path_from_element(self, e):
        if e:
            ns = e.namespace
            n = self._nodes.get(ns)
            if n:
                return self.path_from_element(ns) + (n.index(e),)
            else:
                return ()
        else:
            return ()

    def element_from_path(self, path):
        """
        Get the node form a path. None is returned if no node is found.
        """
        try:
            nodes = self._nodes
            node = None
            for index in path:
                node = nodes[node][index]
            return node
        except IndexError:
            return None

    @component.adapter(IAttributeChangeEvent)
    @catchall
    def _on_element_change(self, event):
        """
        Element changed, update appropriate row.
        """
        element = event.element
        if element not in self._nodes:
            return

        if (
            event.property is UML.Classifier.isAbstract
            or event.property is UML.BehavioralFeature.isAbstract
        ):
            path = self.path_from_element(element)
            if path:
                self.row_changed(path, self.get_iter(path))

        if event.property is UML.NamedElement.name:
            try:
                path = self.path_from_element(element)
            except KeyError:
                # Element not visible in the tree view
                return

            if not path:
                return
            self.row_changed(path, self.get_iter(path))
            parent_nodes = self._nodes[element.namespace]
            parent_path = self.path_from_element(element.namespace)
            if not parent_path:
                return

            original = list(parent_nodes)
            parent_nodes.sort(key=_tree_sorter)
            if parent_nodes != original:
                # reorder the list:
                self.rows_reordered(
                    parent_path,
                    self.get_iter(parent_path),
                    list(map(list.index, [original] * len(parent_nodes), parent_nodes)),
                )

    def _add_elements(self, element):
        """
        Add a single element.
        """
        if type(element) not in self.filter:
            return
        if element.namespace not in self._nodes:
            return

        self._nodes.setdefault(element, [])
        parent = self._nodes[element.namespace]
        parent.append(element)
        parent.sort(key=_tree_sorter)
        path = self.path_from_element(element)
        self.row_inserted(path, self.get_iter(path))

        # Add children
        if isinstance(element, UML.Namespace):
            for e in element.ownedMember:
                # check if owned member is indeed within parent's namespace
                # the check is important in case on Node classes
                if element is e.namespace:
                    self._add_elements(e)

    def _remove_element(self, element):
        """
        Remove elements from the nodes. No update signal is emitted.
        """

        def remove(n):
            for c in self._nodes.get(n, []):
                remove(c)
            try:
                del self._nodes[n]
            except KeyError:
                pass

        remove(element)

    @component.adapter(ElementCreateEvent)
    @catchall
    def _on_element_create(self, event):
        element = event.element
        if event.service is self.factory:
            self._add_elements(element)

    @component.adapter(IElementDeleteEvent)
    @catchall
    def _on_element_delete(self, event):
        element = event.element

        # log.debug('Namespace received deleting element %s' % element)

        if event.service is self.factory and type(element) in self.filter:
            path = self.path_from_element(element)

            # log.debug('Deleting element %s from path %s' % (element, path))

            # Remove all sub-elements:
            if path:
                self.row_deleted(path)
                if path[:-1]:
                    self.row_has_child_toggled(path[:-1], self.get_iter(path[:-1]))
            self._remove_element(element)

            parent_node = self._nodes.get(element.namespace)
            if parent_node:
                parent_node.remove(element)

    #            if path and parent_node and len(self._nodes[parent_node]) == 0:
    #                self.row_has_child_toggled(path[:-1], self.get_iter(path[:-1]))

    @component.adapter(DerivedSetEvent)
    @catchall
    def _on_association_set(self, event):

        element = event.element
        if type(element) not in self.filter:
            return

        if event.property is UML.NamedElement.namespace:
            # Check if the element is actually in the element factory:
            if element not in self.factory:
                return

            old_value, new_value = event.old_value, event.new_value

            # Remove entry from old place
            if old_value in self._nodes:
                try:
                    path = self.path_from_element(old_value) + (
                        self._nodes[old_value].index(element),
                    )
                except ValueError:
                    log.error(
                        "Unable to create path for element %s and old_value %s"
                        % (element, self._nodes[old_value])
                    )
                else:
                    self._nodes[old_value].remove(element)
                    self.row_deleted(path)
                    path = path[:-1]  # self.path_from_element(old_value)
                    if path:
                        self.row_has_child_toggled(path, self.get_iter(path))

            # Add to new place. This may fail if the type of the new place is
            # not in the tree model (because it's filtered)
            log.debug("Trying to add %s to %s" % (element, new_value))
            if new_value in self._nodes:
                if element in self._nodes:
                    parent = self._nodes[new_value]
                    parent.append(element)
                    parent.sort(key=_tree_sorter)
                    path = self.path_from_element(element)
                    self.row_inserted(path, self.get_iter(path))
                else:
                    self._add_elements(element)
            elif element in self._nodes:
                # Non-existent: remove entirely
                self._remove_element(element)

    @component.adapter(ModelFactoryEvent)
    def refresh(self, event=None):
        self.flush()
        self._build_model()

    @component.adapter(FlushFactoryEvent)
    def flush(self, event=None):
        for n in self._nodes[None]:
            self.row_deleted((0,))
        self._nodes = {None: []}

    def _build_model(self):
        toplevel = self.factory.select(
            lambda e: isinstance(e, UML.Namespace) and not e.namespace
        )

        for element in toplevel:
            self._add_elements(element)

    # TreeModel methods:

    def on_get_flags(self):
        """
        Returns the GtkTreeModelFlags for this particular type of model.
        """
        return 0

    def on_get_n_columns(self):
        """
        Returns the number of columns in the model.
        """
        return 1

    def on_get_column_type(self, index):
        """
        Returns the type of a column in the model.
        """
        return GObject.TYPE_PYOBJECT

    def on_get_path(self, node):
        """
        Returns the path for a node as a tuple (0, 1, 1).
        """
        path = self.path_from_element(node)
        return path

    def on_get_iter(self, path):
        """
        Returns the node corresponding to the given path.
        The path is a tuple of values, like (0 1 1). Returns None if no
        iterator can be created.
        """
        return self.element_from_path(path)

    def on_get_value(self, node, column):
        """
        Returns the model element that matches 'node'.
        """
        assert column == 0, "column can only be 0"
        return node

    def on_iter_next(self, node):
        """
        Returns the next node at this level of the tree. None if no
        next element.
        """
        try:
            parent = self._nodes[node.namespace]
            index = parent.index(node)
            return parent[index + 1]
        except (IndexError, ValueError) as e:
            return None

    def on_iter_has_child(self, node):
        """
        Returns true if this node has children, or None.
        """
        n = self._nodes.get(node)
        return n or len(n) > 0

    def on_iter_children(self, node):
        """
        Returns the first child of this node, or None.
        """
        try:
            return self._nodes[node][0]
        except (IndexError, KeyError) as e:
            pass

    def on_iter_n_children(self, node):
        """
        Returns the number of children of this node.
        """
        return len(self._nodes[node])

    def on_iter_nth_child(self, node, n):
        """
        Returns the nth child of this node.
        """
        try:
            nodes = self._nodes[node]
            return nodes[n]
        except TypeError as e:
            return None

    def on_iter_parent(self, node):
        """
        Returns the parent of this node or None if no parent
        """
        return node.namespace

    # TreeDragDest

    def row_drop_possible(self, dest_path, selection_data):
        return True

    def drag_data_received(self, dest, selection_data):
        pass


class NamespaceView(Gtk.TreeView):

    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", 0, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", 0, TARGET_STRING),
        Gtk.TargetEntry.new("gaphor/element-id", 0, TARGET_ELEMENT_ID),
    ]

    def __init__(self, model, factory):
        assert isinstance(
            model, NamespaceModel
        ), "model is not a NamespaceModel (%s)" % str(model)
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
                path = model.path_from_element(element)
                if len(path) > 1:
                    self.expand_row(
                        path=Gtk.TreePath.new_from_indices(path[:-1]), open_all=False
                    )
                selection = self.get_selection()
                selection.select_path(path)


@implementer(IUIComponent, IActionProvider)
class Namespace(object):

    title = _("Namespace")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    element_factory = inject("element_factory")
    ui_manager = inject("ui_manager")
    action_manager = inject("action_manager")

    _menu_xml = """
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
          <separator />
          <menuitem action="tree-view-refresh" />
        </popup>
      </ui>
    """

    def __init__(self):
        self._namespace = None
        self._ui_id = None
        self.action_group = build_action_group(self)

    def open(self):
        widget = self.construct()
        self.component_registry.register_handler(self.expand_root_nodes)
        return widget

    def close(self):
        if self._namespace:
            self._namespace.destroy()
            self._namespace = None

            # TODO: How to ensure stuff is removed properly from services?
            # self.ui_manager.remove_ui(self._ui_id)
        self.component_registry.unregister_handler(self.expand_root_nodes)

    def construct(self):
        self._ui_id = self.ui_manager.add_ui_from_string(self._menu_xml)

        model = NamespaceModel(self.element_factory)
        view = NamespaceView(model, self.element_factory)
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
        self.expand_root_nodes()

        return scrolled_window

    @component.adapter(ModelFactoryEvent)
    def expand_root_nodes(self, event=None):
        """
        """
        # Expand all root elements:
        self._namespace.expand_root_nodes()
        self._on_view_cursor_changed(self._namespace)

    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu = self.ui_manager.get_widget("/namespace-popup")
            menu.popup(None, None, None, event.button, event.time)

    def _on_view_row_activated(self, view, path, column):
        """
        Double click on an element in the tree view.
        """
        self.action_manager.execute("tree-view-open")

    def _on_view_cursor_changed(self, view):
        """
        Another row is selected, execute a dummy action.
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
            self.component_registry.handle(Diagram(element))

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
        self.component_registry.handle(Diagram(diagram))
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

    @action(name="tree-view-refresh", label=_("_Refresh"))
    def tree_view_refresh(self):
        self._namespace.get_model().refresh()


# vim: sw=4:et:ai
