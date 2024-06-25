from __future__ import annotations

import logging

from gi.repository import Gio, GObject, Gtk

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.eventmanager import EventManager
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    NamePropertyPage,
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML.classes.datatype import DataTypeItem
from gaphor.UML.classes.enumeration import EnumerationItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.deployments.connector import ConnectorItem
from gaphor.UML.propertypages import (
    check_button_handlers,
    create_list_store,
    list_item_factory,
    list_view_activated,
    list_view_key_handler,
    text_field_handlers,
    update_list_store,
)

log = logging.getLogger(__name__)


new_builder = new_resource_builder("gaphor.UML.classes")


@PropertyPages.register(UML.NamedElement)
class NamedElementPropertyPage(NamePropertyPage):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject: UML.NamedElement | None, event_manager):
        super().__init__(subject, event_manager)

    def construct(self):
        if (
            not self.subject
            or UML.recipes.is_metaclass(self.subject)
            or isinstance(
                self.subject, (UML.ActivityPartition, UML.ActivityParameterNode)
            )
        ):
            return

        return super().construct()


@PropertyPages.register(UML.Classifier)
class ClassifierPropertyPage(PropertyPageBase):
    order = 15

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        if UML.recipes.is_metaclass(self.subject):
            return

        builder = new_builder(
            "classifier-editor",
            signals={"abstract-changed": (self._on_abstract_change,)},
        )

        abstract = builder.get_object("abstract")
        abstract.set_active(self.subject.isAbstract)

        return builder.get_object("classifier-editor")

    def _on_abstract_change(self, button, gparam):
        with Transaction(self.event_manager):
            self.subject.isAbstract = button.get_active()


@PropertyPages.register(InterfaceItem)
class InterfacePropertyPage(PropertyPageBase):
    """Adapter which shows a property page for an interface view."""

    order = 15

    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder(
            "interface-editor", signals={"folded-changed": (self._on_fold_change,)}
        )

        item = self.item

        connected_items = [
            c.item for c in item.diagram.connections.get_connections(connected=item)
        ]
        disallowed = (ConnectorItem,)
        can_fold = not any(isinstance(i, disallowed) for i in connected_items)

        folded = builder.get_object("folded")
        folded.set_active(item.folded != Folded.NONE)
        folded.set_sensitive(can_fold)

        return builder.get_object("interface-editor")

    def _on_fold_change(self, button, gparam):
        item = self.item

        fold = button.get_active()

        with Transaction(self.event_manager):
            item.folded = Folded.PROVIDED if fold else Folded.NONE


class AttributeView(GObject.Object):
    def __init__(
        self, attr: UML.Property | None, klass: UML.Class, event_manager: EventManager
    ):
        super().__init__()
        self.attr = attr
        self.klass = klass
        self.event_manager = event_manager

    @GObject.Property(type=str, default="")
    def attribute(self):
        return (format(self.attr, note=True) or " ") if self.attr else ""

    @attribute.setter  # type: ignore[no-redef]
    def attribute(self, value):
        with Transaction(self.event_manager):
            if not self.attr:
                if not value:
                    return

                model = self.klass.model
                self.attr = model.create(UML.Property)
                self.klass.ownedAttribute = self.attr
            parse(self.attr, value)

    @GObject.Property(type=bool, default=False)
    def static(self):
        return self.attr.isStatic if self.attr else False

    @static.setter  # type: ignore[no-redef]
    def static(self, value):
        if not self.attr:
            return

        with Transaction(self.event_manager):
            self.attr.isStatic = value

    editing = GObject.Property(type=bool, default=False)

    def empty(self):
        return not self.attr

    def unlink(self):
        if self.attr:
            with Transaction(self.event_manager):
                self.attr.unlink()

    def swap(self, item1, item2):
        return self.klass.ownedAttribute.swap(item1.attr, item2.attr)


def attribute_model(klass: UML.Class, event_manager: EventManager) -> Gio.ListStore:
    return create_list_store(
        AttributeView,
        (a for a in klass.ownedAttribute if not a.association),
        lambda attr: AttributeView(attr, klass, event_manager),
    )


def update_attribute_model(
    store: Gio.ListStore, klass: UML.Class, event_manager: EventManager
) -> None:
    update_list_store(
        store,
        lambda item: item.attr,
        (a for a in klass.ownedAttribute if not a.association),
        lambda attr: AttributeView(attr, klass, event_manager),
    )


# We need a type check here, or all Class subtypes will get this editor
ATTRIBUTES_PAGE_CLASSIFIERS = [
    UML.Class,
    UML.DataType,
    UML.Enumeration,
    UML.Interface,
    UML.PrimitiveType,
    UML.Stereotype,
]

OPERATIONS_PAGE_CLASSIFIERS = list(ATTRIBUTES_PAGE_CLASSIFIERS)


@PropertyPages.register(UML.DataType)
@PropertyPages.register(UML.Class)
@PropertyPages.register(UML.Interface)
class AttributesPage(PropertyPageBase):
    order = 20

    def __init__(self, subject, event_manager: EventManager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        if type(self.subject) not in ATTRIBUTES_PAGE_CLASSIFIERS:
            return

        builder = new_builder(
            "attributes-editor",
            "attributes-info",
            signals={
                "attributes-activated": (list_view_activated,),
                "attributes-key-pressed": (list_view_key_handler,),
                "attributes-info-clicked": (self.on_attributes_info_clicked,),
            },
        )
        self.info = builder.get_object("attributes-info")
        help_link(builder, "attributes-info-icon", "attributes-info")

        column_view: Gtk.ColumnView = builder.get_object("attributes-list")

        for column, factory in zip(
            column_view.get_columns(),
            [
                list_item_factory(
                    "text-field-cell.ui",
                    klass=AttributeView,
                    attribute=AttributeView.attribute,
                    placeholder_text=gettext("New Attribute…"),
                    signal_handlers=text_field_handlers("attribute"),
                ),
                list_item_factory(
                    "check-button-cell.ui",
                    klass=AttributeView,
                    attribute=AttributeView.static,
                    signal_handlers=check_button_handlers("static"),
                ),
            ],
        ):
            column.set_factory(factory)

        self.model = attribute_model(self.subject, self.event_manager)
        selection = Gtk.SingleSelection.new(self.model)
        column_view.set_model(selection)

        if self.watcher:
            self.watcher.watch("ownedAttribute", self.on_attributes_changed)

        return unsubscribe_all_on_destroy(
            builder.get_object("attributes-editor"), self.watcher
        )

    def on_attributes_changed(self, event):
        update_attribute_model(self.model, self.subject, self.event_manager)

    def on_attributes_info_clicked(self, image, event):
        self.info.set_visible(True)


@PropertyPages.register(DataTypeItem)
@PropertyPages.register(ClassItem)
@PropertyPages.register(EnumerationItem)
@PropertyPages.register(InterfaceItem)
class ShowAttributesPage(PropertyPageBase):
    order = 21

    def __init__(self, item, event_manager: EventManager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder(
            "show-attributes-editor",
            signals={
                "show-attributes-changed": (self.on_show_attributes_changed,),
            },
        )

        show_attributes = builder.get_object("show-attributes")
        show_attributes.set_active(self.item.show_attributes)

        return builder.get_object("show-attributes-editor")

    def on_show_attributes_changed(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_attributes = button.get_active()


class OperationView(GObject.Object):
    def __init__(
        self, oper: UML.Operation | None, klass: UML.Class, event_manager: EventManager
    ):
        super().__init__()
        self.oper = oper
        self.klass = klass
        self.event_manager = event_manager

    @GObject.Property(type=str, default="")
    def operation(self):
        return (format(self.oper, note=True) or " ") if self.oper else ""

    @operation.setter  # type: ignore[no-redef]
    def operation(self, value):
        with Transaction(self.event_manager):
            if not self.oper:
                if not value:
                    return

                model = self.klass.model
                self.oper = model.create(UML.Operation)
                self.klass.ownedOperation = self.oper
            parse(self.oper, value)

    @GObject.Property(type=bool, default=False)
    def static(self):
        return self.oper.isStatic if self.oper else False

    @static.setter  # type: ignore[no-redef]
    def static(self, value):
        if not self.oper:
            return

        with Transaction(self.event_manager):
            self.oper.isStatic = value

    @GObject.Property(type=bool, default=False)
    def abstract(self):
        return self.oper.isAbstract if self.oper else False

    @abstract.setter  # type: ignore[no-redef]
    def abstract(self, value):
        if not self.oper:
            return

        with Transaction(self.event_manager):
            self.oper.isAbstract = value

    editing = GObject.Property(type=bool, default=False)

    def empty(self):
        return not self.oper

    def unlink(self):
        if self.oper:
            with Transaction(self.event_manager):
                self.oper.unlink()

    def swap(self, item1, item2):
        return self.klass.ownedOperation.swap(item1.oper, item2.oper)


def operation_model(klass: UML.Class, event_manager: EventManager) -> Gio.ListStore:
    return create_list_store(
        OperationView,
        klass.ownedOperation,
        lambda oper: OperationView(oper, klass, event_manager),
    )


def update_operation_model(
    store: Gio.ListStore, klass: UML.Class, event_manager: EventManager
) -> None:
    update_list_store(
        store,
        lambda item: item.oper,
        klass.ownedOperation,
        lambda oper: OperationView(oper, klass, event_manager),
    )


@PropertyPages.register(UML.DataType)
@PropertyPages.register(UML.Class)
@PropertyPages.register(UML.Interface)
class OperationsPage(PropertyPageBase):
    order = 30

    def __init__(self, subject, event_manager: EventManager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        if type(self.subject) not in OPERATIONS_PAGE_CLASSIFIERS:
            return

        builder = new_builder(
            "operations-editor",
            "operations-info",
            signals={
                "operations-activated": (list_view_activated,),
                "operations-key-pressed": (list_view_key_handler,),
                "operations-info-clicked": (self.on_operations_info_clicked,),
            },
        )

        self.info = builder.get_object("operations-info")
        help_link(builder, "operations-info-icon", "operations-info")

        column_view: Gtk.ColumnView = builder.get_object("operations-list")

        for column, factory in zip(
            column_view.get_columns(),
            [
                list_item_factory(
                    "text-field-cell.ui",
                    klass=OperationView,
                    attribute=OperationView.operation,
                    placeholder_text=gettext("New Operation…"),
                    signal_handlers=text_field_handlers("operation"),
                ),
                list_item_factory(
                    "check-button-cell.ui",
                    klass=OperationView,
                    attribute=OperationView.abstract,
                    signal_handlers=check_button_handlers("abstract"),
                ),
                list_item_factory(
                    "check-button-cell.ui",
                    klass=OperationView,
                    attribute=OperationView.static,
                    signal_handlers=check_button_handlers("static"),
                ),
            ],
        ):
            column.set_factory(factory)

        self.model = operation_model(self.subject, self.event_manager)
        selection = Gtk.SingleSelection.new(self.model)
        column_view.set_model(selection)

        if self.watcher:
            self.watcher.watch("ownedOperation", self.on_operations_changed)

        return unsubscribe_all_on_destroy(
            builder.get_object("operations-editor"), self.watcher
        )

    def on_operations_changed(self, event):
        update_operation_model(self.model, self.subject, self.event_manager)

    def on_operations_info_clicked(self, image, event):
        self.info.set_visible(True)


@PropertyPages.register(DataTypeItem)
@PropertyPages.register(EnumerationItem)
@PropertyPages.register(ClassItem)
@PropertyPages.register(InterfaceItem)
class ShowOperationsPage(PropertyPageBase):
    order = 31

    def __init__(self, item, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder(
            "show-operations-editor",
            signals={
                "show-operations-changed": (self.on_show_operations_changed,),
            },
        )

        show_operations = builder.get_object("show-operations")
        show_operations.set_active(self.item.show_operations)

        return builder.get_object("show-operations-editor")

    def on_show_operations_changed(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_operations = button.get_active()


@PropertyPages.register(UML.Component)
class ComponentPropertyPage(PropertyPageBase):
    order = 15

    subject: UML.Component

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "component-editor",
            signals={"indirectly-instantiated-changed": (self._on_ii_change,)},
        )

        ii = builder.get_object("indirectly-instantiated")
        ii.set_active(subject.isIndirectlyInstantiated)

        return builder.get_object("component-editor")

    def _on_ii_change(self, button, gparam):
        """Called when user clicks "Indirectly instantiated" check button."""
        if subject := self.subject:
            with Transaction(self.event_manager):
                subject.isIndirectlyInstantiated = button.get_active()
