"""Stereotype property page."""
from unicodedata import normalize

from gi.repository import Gdk, Gio, GLib, GObject, Gtk

from gaphor import UML
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Element, Presentation
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.i18n import gettext, translated_ui_string
from gaphor.transaction import Transaction
from gaphor.UML.profiles.metaclasspropertypage import new_builder
from gaphor.UML.propertypages import text_field_handlers


@PropertyPages.register(Element)
class StereotypePage(PropertyPageBase):
    order = 40

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        subject = self.subject
        if isinstance(subject, Presentation):
            subject = subject.subject

        if not subject:
            return None

        stereotypes = UML.recipes.get_stereotypes(subject)
        if not stereotypes:
            return None

        builder = new_builder(
            "stereotypes-editor",
            signals={
                "stereotype-activated": (stereotype_activated,),
                "stereotype-key-pressed": (stereotype_key_handler,),
            },
        )

        stereotype_list = builder.get_object("stereotype-list")
        model = stereotype_model(subject, self.event_manager)

        stereotype_set_model_with_interaction(stereotype_list, model)

        return builder.get_object("stereotypes-editor")


@PropertyPages.register(Presentation)
class ShowStereotypePage(PropertyPageBase):
    order = 41

    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        subject = self.item.subject
        if not subject or not hasattr(self.item, "show_stereotypes"):
            return None

        stereotypes = UML.recipes.get_stereotypes(subject)
        if not stereotypes:
            return None

        builder = new_builder(
            "show-stereotypes-editor",
            signals={
                "show-stereotypes-changed": (self._on_show_stereotypes_change,),
            },
        )

        show_stereotypes = builder.get_object("show-stereotypes")
        show_stereotypes.set_active(self.item.show_stereotypes)

        return builder.get_object("show-stereotypes-editor")

    def _on_show_stereotypes_change(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_stereotypes = button.get_active()


def stereotype_set_model_with_interaction(stereotype_list, model):
    def on_stereotype_toggled(cell):
        button = cell.get_child().get_first_child()
        view = cell.get_item()
        view.applied = button.get_active()
        update_stereotype_model(model)

    for column, factory in zip(
        stereotype_list.get_columns(),
        [
            name_list_item_factory(
                signal_handlers={
                    "on_toggled": (on_stereotype_toggled,),
                },
            ),
            value_list_item_factory(
                signal_handlers=text_field_handlers("slot_value"),
            ),
        ],
    ):
        column.set_factory(factory)

    selection = Gtk.SingleSelection.new(model)
    stereotype_list.set_model(selection)


class StereotypeView(GObject.Object):
    def __init__(
        self,
        target: Element,
        stereotype: UML.Stereotype,
        attr: UML.Property | None,
        event_manager: EventManager,
    ):
        super().__init__()
        self.stereotype = stereotype
        self.target = target
        self.attr = attr
        self.event_manager = event_manager

    @property
    def instance(self):
        return stereotype_application(self.stereotype, self.target)

    @property
    def slot(self):
        instance = self.instance
        attr = self.attr
        return (
            next(
                (slot for slot in instance.slot if slot.definingFeature is attr),
                None,
            )
            if instance
            else None
        )

    editing = GObject.Property(type=bool, default=False)

    @GObject.Property(type=str, default="", flags=GObject.ParamFlags.READABLE)
    def name(self):
        return (self.attr.name if self.attr else self.stereotype.name) or ""

    @GObject.Property(type=bool, default=False)
    def applied(self):
        return bool(self.instance)

    @applied.setter  # type: ignore[no-redef]
    def applied(self, value):
        instance = self.instance
        with Transaction(self.event_manager):
            if value and not instance:
                UML.recipes.apply_stereotype(self.target, self.stereotype)
            elif not value and instance:
                UML.recipes.remove_stereotype(self.target, self.stereotype)

    @GObject.Property(type=bool, default=False)
    def checkbox_visible(self):
        return not bool(self.attr)

    @GObject.Property(type=str)
    def placeholder_text(self):
        return gettext("New Slot Value…") if self.attr and self.instance else ""

    @GObject.Property(type=bool, default=False)
    def can_edit(self):
        return bool(self.attr and self.instance)

    @GObject.Property(type=GObject.TYPE_STRV)
    def indent_classes(self):
        return ["stereotype-value"] if self.attr else []

    @GObject.Property(type=bool, default=True)
    def sensitive(self):
        return not self.attr or self.instance

    @GObject.Property(type=str)
    def slot_value(self):
        slot = self.slot
        return slot.value if slot else ""

    @slot_value.setter  # type: ignore[no-redef]
    def slot_value(self, value):
        slot = self.slot
        with Transaction(self.event_manager):
            if value:
                if slot is None:
                    slot = UML.recipes.add_slot(self.instance, self.attr)
                slot.value = value
            elif slot:
                del self.instance.slot[slot]


def stereotype_model(subject: Element, event_manager: EventManager):
    model = Gio.ListStore.new(StereotypeView.__gtype__)
    stereotypes = UML.recipes.get_stereotypes(subject)

    for st in sorted(
        stereotypes, key=lambda s: normalize("NFC", s.name or "").casefold()
    ):
        model.append(StereotypeView(subject, st, None, event_manager))

        for attr in all_attributes(st):
            model.append(StereotypeView(subject, st, attr, event_manager))

    return model


def update_stereotype_model(store: Gio.ListStore):
    for view in store:
        view.notify("placeholder_text")
        view.notify("can_edit")
        view.notify("slot_value")
        view.notify("sensitive")


def all_attributes(stereotype, seen=None):
    if seen is None:
        seen = {stereotype}

    for super_type in stereotype.generalization[:].general[:]:
        if super_type not in seen:
            seen.add(super_type)
            yield from all_attributes(super_type)
    yield from (attr for attr in stereotype.ownedAttribute if not attr.association)


def stereotype_application(st, subject) -> UML.InstanceSpecification | None:
    return next(
        (applied for applied in subject.appliedStereotype if st in applied.classifier),
        None,
    )


def name_list_item_factory(signal_handlers=None):
    ui_string = translated_ui_string("gaphor.UML.profiles", "stereotype-name-cell.ui")

    return Gtk.BuilderListItemFactory.new_from_bytes(
        Gtk.Builder.BuilderScope(signal_handlers),
        GLib.Bytes.new(ui_string.encode("utf-8")),
    )


def value_list_item_factory(signal_handlers=None):
    ui_string = translated_ui_string("gaphor.UML.profiles", "stereotype-value-cell.ui")

    return Gtk.BuilderListItemFactory.new_from_bytes(
        Gtk.Builder.BuilderScope(signal_handlers),
        GLib.Bytes.new(ui_string.encode("utf-8")),
    )


def stereotype_activated(list_view, _row):
    selection = list_view.get_model()
    item = selection.get_selected_item()

    if item.attr:
        item.editing = True
    else:
        item.applied = not item.applied


def stereotype_key_handler(ctrl, keyval, _keycode, state):
    list_view = ctrl.get_widget()
    selection = list_view.get_model()
    item = selection.get_selected_item()

    if keyval in (Gdk.KEY_F2,):
        item.editing = True
        return True

    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace) and not state & (
        Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
    ):
        item.slot_value = ""
        return True

    return False
