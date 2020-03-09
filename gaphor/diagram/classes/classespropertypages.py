import importlib
import logging
from inspect import isclass

from gaphas.decorators import AsyncIO
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.interface import Folded, InterfaceItem
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.components.connector import ConnectorItem
from gaphor.diagram.propertypages import (
    EditableTreeModel,
    NamedElementPropertyPage,
    NamedItemPropertyPage,
    PropertyPageBase,
    PropertyPages,
    UMLComboModel,
    builder,
    create_hbox_label,
    create_tree_view,
    create_uml_combo,
    on_bool_cell_edited,
    on_keypress_event,
    on_text_cell_edited,
)

log = logging.getLogger(__name__)


class ClassAttributes(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def _get_rows(self):
        for attr in self._item.subject.ownedAttribute:
            if not attr.association:
                yield [UML.format(attr), attr.isStatic, attr]

    def _create_object(self):
        attr = self._item.model.create(UML.Property)
        self._item.subject.ownedAttribute = attr
        return attr

    @transactional
    def _set_object_value(self, row, col, value):
        attr = row[-1]
        if col == 0:
            UML.parse(attr, value)
            row[0] = UML.format(attr)
        elif col == 1:
            attr.isStatic = not attr.isStatic
            row[1] = attr.isStatic
        elif col == 2:
            # Value in attribute object changed:
            row[0] = UML.format(attr)
            row[1] = attr.isStatic

    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedAttribute.swap(o1, o2)


class ClassOperations(EditableTreeModel):
    """GTK tree model to edit class operations."""

    def _get_rows(self):
        for operation in self._item.subject.ownedOperation:
            yield [
                UML.format(operation),
                operation.isAbstract,
                operation.isStatic,
                operation,
            ]

    def _create_object(self):
        operation = self._item.model.create(UML.Operation)
        self._item.subject.ownedOperation = operation
        return operation

    @transactional
    def _set_object_value(self, row, col, value):
        operation = row[-1]
        if col == 0:
            UML.parse(operation, value)
            row[0] = UML.format(operation)
        elif col == 1:
            operation.isAbstract = not operation.isAbstract
            row[1] = operation.isAbstract
        elif col == 2:
            operation.isStatic = not operation.isStatic
            row[2] = operation.isStatic
        elif col == 3:
            row[0] = UML.format(operation)
            row[1] = operation.isAbstract
            row[2] = operation.isStatic

    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedOperation.swap(o1, o2)


def _issubclass(c, b):
    try:
        return issubclass(c, b)
    except TypeError:
        return False


@PropertyPages.register(UML.Class)
class ClassPropertyPage(NamedElementPropertyPage):
    """Adapter which shows a property page for a class view.
    Also handles metaclasses.
    """

    subject: UML.Class

    CLASSES = list(
        sorted(
            c
            for c in dir(UML)
            if _issubclass(getattr(UML, c), UML.Element) and c != "Stereotype"
        )
    )

    def __init__(self, subject):
        super().__init__(subject)

    def construct(self):
        if UML.model.is_metaclass(self.subject):
            return self.construct_metaclass()

        page = super().construct()

        if not self.subject:
            return page

        # Abstract toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)
        button = Gtk.CheckButton(label=gettext("Abstract"))
        button.set_active(self.subject.isAbstract)

        button.connect("toggled", self._on_abstract_change)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        return page

    @transactional
    def _on_abstract_change(self, button):
        self.subject.isAbstract = button.get_active()

    def construct_metaclass(self):
        page = Gtk.VBox()

        subject = self.subject
        if not subject:
            return page

        hbox = create_hbox_label(self, page, gettext("Name"))
        model = Gtk.ListStore(str)
        for c in self.CLASSES:
            model.append([c])

        cb = Gtk.ComboBox.new_with_model_and_entry(model)

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)
        cb.get_child().set_completion(completion)

        entry = cb.get_child()
        entry.set_text(subject and subject.name or "")
        hbox.pack_start(cb, True, True, 0)
        page.default = entry

        # monitor subject.name attribute
        changed_id = entry.connect("changed", self._on_name_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.handler_block(changed_id)
                entry.set_text(event.new_value)
                entry.handler_unblock(changed_id)

        self.watcher.watch("name", handler).subscribe_all()
        entry.connect("destroy", self.watcher.unsubscribe_all)
        page.show_all()
        return page


@PropertyPages.register(InterfaceItem)
class InterfacePropertyPage(NamedItemPropertyPage):
    """Adapter which shows a property page for an interface view."""

    def construct(self):
        page = super().construct()
        item = self.item

        # Fold toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(gettext("Folded"))
        button.set_active(item.folded != Folded.NONE)
        button.connect("toggled", self._on_fold_change)

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        disallowed = (ConnectorItem,)
        can_fold = not any(map(lambda i: isinstance(i, disallowed), connected_items))

        button.set_sensitive(can_fold)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        return page

    @transactional
    def _on_fold_change(self, button):
        item = self.item

        fold = button.get_active()

        if fold:
            item.folded = Folded.PROVIDED
        else:
            item.folded = Folded.NONE


@PropertyPages.register(ClassItem)
@PropertyPages.register(InterfaceItem)
class AttributesPage(PropertyPageBase):
    """An editor for attributes associated with classes and interfaces."""

    order = 20
    name = "Attributes"

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()
        self.builder = builder("attributes-editor")

    def construct(self):
        if not self.item.subject:
            return

        page = self.builder.get_object("attributes-editor")

        show_attributes = self.builder.get_object("show-attributes")
        show_attributes.set_active(self.item.show_attributes)

        self.model = ClassAttributes(self.item, (str, bool, object))

        tree_view: Gtk.TreeView = self.builder.get_object("attributes-list")
        tree_view.set_model(self.model)

        def handler(event):
            print("should update model here")

        self.watcher.watch("ownedAttribute.name", handler).watch(
            "ownedAttribute.isDerived", handler
        ).watch("ownedAttribute.visibility", handler).watch(
            "ownedAttribute.isStatic", handler
        ).watch(
            "ownedAttribute.lowerValue", handler
        ).watch(
            "ownedAttribute.upperValue", handler
        ).watch(
            "ownedAttribute.defaultValue", handler
        ).watch(
            "ownedAttribute.typeValue", handler
        ).subscribe_all()

        self.builder.connect_signals(
            {
                "show-attributes-changed": (self._on_show_attributes_change,),
                "attributes-name-edited": (on_text_cell_edited, self.model, 0),
                "attributes-static-edited": (on_bool_cell_edited, self.model, 1),
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
                "attributes-keypress": (on_keypress_event,),
            }
        )
        return page

    @transactional
    def _on_show_attributes_change(self, button):
        self.item.show_attributes = button.get_active()
        self.item.request_update()


@PropertyPages.register(ClassItem)
@PropertyPages.register(InterfaceItem)
class OperationsPage(PropertyPageBase):
    """An editor for operations associated with classes and interfaces."""

    order = 30
    name = "Operations"

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()
        self.builder = builder("operations-editor")

    def construct(self):
        if not self.item.subject:
            return

        page = self.builder.get_object("operations-editor")

        show_operations = self.builder.get_object("show-operations")
        show_operations.set_active(self.item.show_operations)

        self.model = ClassOperations(self.item, (str, bool, bool, object))

        tree_view: Gtk.TreeView = self.builder.get_object("operations-list")
        tree_view.set_model(self.model)

        def handler(event):
            print("TODO: operations handler")

        self.watcher.watch("ownedOperation.name", handler).watch(
            "ownedOperation.isAbstract", handler
        ).watch("ownedOperation.visibility", handler).watch(
            "ownedOperation.returnResult.lowerValue", handler
        ).watch(
            "ownedOperation.returnResult.upperValue", handler
        ).watch(
            "ownedOperation.returnResult.typeValue", handler
        ).watch(
            "ownedOperation.formalParameter.lowerValue", handler
        ).watch(
            "ownedOperation.formalParameter.upperValue", handler
        ).watch(
            "ownedOperation.formalParameter.typeValue", handler
        ).watch(
            "ownedOperation.formalParameter.defaultValue", handler
        ).subscribe_all()

        self.builder.connect_signals(
            {
                "show-operations-changed": (self._on_show_operations_change,),
                "operations-name-edited": (on_text_cell_edited, self.model, 0),
                "operations-abstract-edited": (on_bool_cell_edited, self.model, 1),
                "operations-static-edited": (on_bool_cell_edited, self.model, 2),
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
                "operations-keypress": (on_keypress_event,),
            }
        )

        return page

    @transactional
    def _on_show_operations_change(self, button):
        self.item.show_operations = button.get_active()
        self.item.request_update()


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 0

    DEPENDENCY_TYPES = (
        (gettext("Dependency"), UML.Dependency),
        (gettext("Usage"), UML.Usage),
        (gettext("Realization"), UML.Realization),
        (gettext("Implementation"), UML.Implementation),
    )

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.watcher = self.item.watcher()
        self.builder = builder("dependency-editor")

    def construct(self):
        page = self.builder.get_object("dependency-editor")

        dependency_combo = self.builder.get_object("dependency-combo")
        model = UMLComboModel(self.DEPENDENCY_TYPES)
        dependency_combo.set_model(model)

        automatic = self.builder.get_object("automatic")
        automatic.set_active(self.item.auto_dependency)

        self.update()

        self.watcher.watch("subject", self._on_subject_change).subscribe_all()

        self.builder.connect_signals(
            {
                "dependency-type-changed": (self._on_dependency_type_change,),
                "automatic-changed": (self._on_auto_dependency_change,),
                "dependency-type-destroy": (self.watcher.unsubscribe_all,),
            }
        )

        return page

    def _on_subject_change(self, event):
        self.update()

    def update(self):
        """
        Update dependency type combo box.

        Disallow dependency type when dependency is established.
        """
        combo = self.builder.get_object("dependency-combo")
        if combo.get_model():
            item = self.item
            index = combo.get_model().get_index(item.dependency_type)
            combo.props.sensitive = not item.auto_dependency
            combo.set_active(index)

    @transactional
    def _on_dependency_type_change(self, combo):
        combo = self.builder.get_object("dependency-combo")
        cls = combo.get_model().get_value(combo.get_active())
        self.item.dependency_type = cls
        subject = self.item.subject
        if subject:
            UML.model.swap_element(subject, cls)
            self.item.request_update()

    @transactional
    def _on_auto_dependency_change(self, button):
        self.item.auto_dependency = button.get_active()
        self.update()


@PropertyPages.register(AssociationItem)
class AssociationPropertyPage(NamedItemPropertyPage):
    """
    """

    def construct_end(self, title, end):

        if not end.subject:
            return None

        frame = Gtk.Frame.new(f"{title} (: {end.subject.type.name})")
        vbox = Gtk.VBox()
        vbox.set_border_width(6)
        vbox.set_spacing(6)
        frame.add(vbox)

        self.create_pages(end, vbox)

        return frame

    def construct(self):
        page = super().construct()

        if not self.subject:
            return page

        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(label=gettext("Show direction"))
        button.set_active(self.item.show_direction)
        button.connect("toggled", self._on_show_direction_change)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_from_icon_name(
            "object-flip-horizontal-symbolic", Gtk.IconSize.BUTTON
        )
        button.connect("clicked", self._on_invert_direction_change)
        hbox.pack_start(button, True, True, 0)

        page.pack_start(hbox, False, True, 0)

        box = self.construct_end(gettext("Head"), self.item.head_end)
        if box:
            page.pack_start(box, False, True, 0)

        box = self.construct_end(gettext("Tail"), self.item.tail_end)
        if box:
            page.pack_start(box, False, True, 0)

        return page

    @transactional
    def _on_show_direction_change(self, button):
        self.item.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.item.invert_direction()

    def get_adapters(self, item):
        """
        Return an ordered list of (order, name, adapter).
        """
        adaptermap = {}
        try:
            if item.subject:
                for adapter in PropertyPages(item.subject):
                    adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)
        except AttributeError:
            pass
        for adapter in PropertyPages(item):
            adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)

        adapters = sorted(adaptermap.values())
        return adapters

    def create_pages(self, item, vbox):
        """
        Load all tabs that can operate on the given item.

        The first item will not contain a title.
        """
        adapters = self.get_adapters(item)

        first = True
        for _, name, adapter in adapters:
            try:
                page = adapter.construct()
                if page is None:
                    continue
                if first:
                    vbox.pack_start(page, False, True, 0)
                    first = False
                else:
                    expander = Gtk.Expander()
                    expander.set_use_markup(True)
                    expander.set_label(f"<b>{name}</b>")
                    expander.add(page)
                    expander.show_all()
                    vbox.pack_start(expander, False, True, 0)
            except Exception:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )


@PropertyPages.register(UML.Property)
class AssociationEndPropertyPage(PropertyPageBase):
    """Property page for association end properties."""

    order = 0

    NAVIGABILITY = [None, False, True]

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject and subject.watcher()

    def construct(self):
        vbox = Gtk.VBox()
        entry = Gtk.Entry()
        # entry.set_text(UML.format(self.subject, visibility=True, is_derived=Truemultiplicity=True) or '')

        # monitor subject attribute (all, cause it contains many children)
        changed_id = entry.connect("changed", self._on_end_name_change)

        def handler(event):
            if not entry.props.has_focus:
                entry.handler_block(changed_id)
                entry.set_text(
                    UML.format(
                        self.subject,
                        visibility=True,
                        is_derived=True,
                        multiplicity=True,
                    )
                    or ""
                )
                # entry.set_text(UML.format(self.subject, multiplicity=True) or '')
                entry.handler_unblock(changed_id)

        handler(None)

        self.watcher.watch("name", handler).watch("aggregation", handler).watch(
            "visibility", handler
        ).watch("lowerValue", handler).watch("upperValue", handler).subscribe_all()
        entry.connect("destroy", self.watcher.unsubscribe_all)

        vbox.pack_start(entry, True, True, 0)

        entry.set_tooltip_text(
            """\
Enter attribute name and multiplicity, for example
- name
+ name [1]
- name [1..2]
~ 1..2
- [1..2]\
"""
        )

        combo = Gtk.ComboBoxText()
        for t in ("Unknown navigation", "Not navigable", "Navigable"):
            combo.append_text(t)

        nav = self.subject.navigability
        combo.set_active(self.NAVIGABILITY.index(nav))

        combo.connect("changed", self._on_navigability_change)
        vbox.pack_start(combo, False, True, 0)

        combo = Gtk.ComboBoxText()
        for t in ("No aggregation", "Shared", "Composite"):
            combo.append_text(t)

        combo.set_active(
            ["none", "shared", "composite"].index(self.subject.aggregation)
        )

        combo.connect("changed", self._on_aggregation_change)
        vbox.pack_start(combo, False, True, 0)

        return vbox

    @transactional
    def _on_end_name_change(self, entry):
        UML.parse(self.subject, entry.get_text())

    @transactional
    def _on_navigability_change(self, combo):
        nav = self.NAVIGABILITY[combo.get_active()]
        UML.model.set_navigability(self.subject.association, self.subject, nav)

    @transactional
    def _on_aggregation_change(self, combo):
        self.subject.aggregation = ("none", "shared", "composite")[combo.get_active()]
