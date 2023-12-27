"""Stereotype property page."""
from unicodedata import normalize

from gi.repository import Gdk, Gio, GLib, GObject, Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.modeling.element import Element
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.i18n import gettext, translated_ui_string
from gaphor.UML.profiles.metaclasspropertypage import new_builder
from gaphor.UML.propertypages import text_field_handlers


@PropertyPages.register(UML.Element)
class StereotypePage(PropertyPageBase):
    order = 40

    def __init__(self, item):
        self.item = item

    def construct(self):
        subject = self.item.subject
        if not subject:
            return None

        stereotypes = UML.recipes.get_stereotypes(subject)
        if not stereotypes:
            return None

        builder = new_builder(
            "stereotypes-editor",
            signals={
                "show-stereotypes-changed": (self._on_show_stereotypes_change,),
                "stereotype-key-pressed": (stereotype_key_handler,),
            },
        )

        show_stereotypes = builder.get_object("show-stereotypes")

        if hasattr(self.item, "show_stereotypes"):
            show_stereotypes.set_active(self.item.show_stereotypes)
        else:
            show_stereotypes.get_parent().unparent()

        stereotype_list = builder.get_object("stereotype-list")
        model = stereotype_model(subject)

        stereotype_set_model_with_interaction(stereotype_list, model)

        return builder.get_object("stereotypes-editor")

    @transactional
    def _on_show_stereotypes_change(self, button, gparam):
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
    ):
        super().__init__()
        self.stereotype = stereotype
        self.target = target
        self.attr = attr

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
        return self.attr.name or "" if self.attr else self.stereotype.name or ""

    @GObject.Property(type=bool, default=False)
    def applied(self):
        return bool(self.instance)

    @applied.setter  # type: ignore[no-redef]
    @transactional
    def applied(self, value):
        instance = self.instance
        if value and not instance:
            UML.recipes.apply_stereotype(self.target, self.stereotype)
        elif instance:
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
    @transactional
    def slot_value(self, value):
        slot = self.slot
        if value:
            if slot is None:
                slot = UML.recipes.add_slot(self.instance, self.attr)
            slot.value = value
        elif slot:
            del self.instance.slot[slot]

    def start_editing(self):
        self.editing = True


def stereotype_model(subject: Element):
    model = Gio.ListStore.new(StereotypeView.__gtype__)
    stereotypes = UML.recipes.get_stereotypes(subject)

    for st in sorted(
        stereotypes, key=lambda s: normalize("NFC", s.name or "").casefold()
    ):
        model.append(StereotypeView(subject, st, None))

        for attr in all_attributes(st):
            model.append(StereotypeView(subject, st, attr))

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


@transactional
def stereotype_key_handler(ctrl, keyval, _keycode, state):
    list_view = ctrl.get_widget()
    selection = list_view.get_model()
    item = selection.get_selected_item()

    if keyval in (Gdk.KEY_F2,):
        item.start_editing()
        return True

    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace) and not state & (
        Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
    ):
        item.slot_value = ""
        return True

    return False
