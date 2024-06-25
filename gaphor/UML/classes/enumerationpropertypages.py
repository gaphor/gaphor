from gi.repository import Gio, GObject, Gtk

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.eventmanager import EventManager
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML.classes.classespropertypages import new_resource_builder
from gaphor.UML.classes.enumeration import EnumerationItem
from gaphor.UML.propertypages import (
    create_list_store,
    list_item_factory,
    list_view_activated,
    list_view_key_handler,
    text_field_handlers,
    update_list_store,
)

new_builder = new_resource_builder("gaphor.UML.classes")


class EnumerationView(GObject.Object):
    def __init__(
        self,
        literal: UML.EnumerationLiteral | None,
        enum: UML.Enumeration,
        event_manager: EventManager,
    ):
        super().__init__()
        self.literal = literal
        self.enum = enum
        self.event_manager = event_manager

    @GObject.Property(type=str, default="")
    def enumeration(self):
        return (format(self.literal, note=True) or " ") if self.literal else ""

    @enumeration.setter  # type: ignore[no-redef]
    def enumeration(self, value):
        with Transaction(self.event_manager):
            if not self.literal:
                if not value:
                    return

                model = self.enum.model
                self.literal = model.create(UML.EnumerationLiteral)
                self.enum.ownedLiteral = self.literal
            parse(self.literal, value)

    editing = GObject.Property(type=bool, default=False)

    def empty(self):
        return not self.literal

    def unlink(self):
        if self.literal:
            with Transaction(self.event_manager):
                self.literal.unlink()

    def swap(self, item1, item2):
        return self.enum.ownedLiteral.swap(item1.literal, item2.literal)


def enumeration_model(
    enum: UML.Enumeration, event_manager: EventManager
) -> Gio.ListStore:
    return create_list_store(
        EnumerationView,
        enum.ownedLiteral,
        lambda literal: EnumerationView(literal, enum, event_manager),
    )


def update_enumeration_model(
    store: Gio.ListStore, enum: UML.Enumeration, event_manager: EventManager
) -> None:
    update_list_store(
        store,
        lambda item: item.literal,
        enum.ownedLiteral,
        lambda literal: EnumerationView(literal, enum, event_manager),
    )


@PropertyPages.register(UML.Enumeration)
class EnumerationPage(PropertyPageBase):
    """An editor for enumeration literals for an enumeration."""

    order = 18

    def __init__(self, subject, event_manager: EventManager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        if not isinstance(self.subject, UML.Enumeration):
            return

        builder = new_builder(
            "enumerations-editor",
            "enumerations-info",
            signals={
                "enumerations-activated": (list_view_activated,),
                "enumerations-key-pressed": (list_view_key_handler,),
                "enumerations-info-clicked": (self.on_enumerations_info_clicked,),
            },
        )

        self.info = builder.get_object("enumerations-info")
        help_link(builder, "enumerations-info-icon", "enumerations-info")

        column_view: Gtk.ColumnView = builder.get_object("enumerations-list")

        for column, factory in zip(
            column_view.get_columns(),
            [
                list_item_factory(
                    "text-field-cell.ui",
                    klass=EnumerationView,
                    attribute=EnumerationView.enumeration,
                    placeholder_text=gettext("New Enumeration…"),
                    signal_handlers=text_field_handlers("enumeration"),
                ),
            ],
        ):
            column.set_factory(factory)

        self.model = enumeration_model(self.subject, self.event_manager)
        selection = Gtk.SingleSelection.new(self.model)
        column_view.set_model(selection)

        if self.watcher:
            self.watcher.watch("ownedLiteral", self.on_enumerations_changed)

        return unsubscribe_all_on_destroy(
            builder.get_object("enumerations-editor"), self.watcher
        )

    def on_enumerations_changed(self, event):
        update_enumeration_model(self.model, self.subject, self.event_manager)

    def on_enumerations_info_clicked(self, image, event):
        self.info.set_visible(True)


@PropertyPages.register(EnumerationItem)
class ShowEnumerationPage(PropertyPageBase):
    """An editor for enumeration literals for an enumeration."""

    order = 19

    def __init__(self, item, event_manager: EventManager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not isinstance(self.item.subject, UML.Enumeration):
            return

        builder = new_builder(
            "show-enumerations-editor",
            signals={
                "show-enumerations-changed": (self.on_show_enumerations_changed,),
            },
        )

        show_enumerations = builder.get_object("show-enumerations")
        show_enumerations.set_active(self.item.show_enumerations)

        return builder.get_object("show-enumerations-editor")

    def on_show_enumerations_changed(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_enumerations = button.get_active()
