"""Stereotype property page."""
from gi.repository import Gio, GLib, GObject, Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.modeling.element import Element
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.i18n import gettext, translated_ui_string
from gaphor.UML.profiles.metaclasspropertypage import new_builder
from gaphor.UML.propertypages import list_item_factory, text_field_handlers


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

        # model, toggle_stereotype_handler, set_slot_value_handler = stereotype_model(
        model = stereotype_model(subject)

        builder = new_builder(
            "stereotypes-editor",
            signals={
                "show-stereotypes-changed": (self._on_show_stereotypes_change,),
                # "toggle-stereotype": toggle_stereotype_handler,
                # "set-slot-value": set_slot_value_handler,
            },
        )

        show_stereotypes = builder.get_object("show-stereotypes")

        if hasattr(self.item, "show_stereotypes"):
            show_stereotypes.set_active(self.item.show_stereotypes)
        else:
            show_stereotypes.unparent()

        stereotype_list = builder.get_object("stereotype-list")

        for column, factory in zip(
            stereotype_list.get_columns(),
            [
                name_list_item_factory(
                    signal_handlers=None,
                ),
                value_list_item_factory(
                    signal_handlers=None,
                ),
            ],
        ):
            column.set_factory(factory)

        selection = Gtk.SingleSelection.new(model)
        stereotype_list.set_model(selection)

        return builder.get_object("stereotypes-editor")

    @transactional
    def _on_show_stereotypes_change(self, button, gparam):
        self.item.show_stereotypes = button.get_active()


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
        st = self.stereotype
        return next(
            (
                applied
                for applied in self.target.appliedStereotype
                if st in applied.classifier
            ),
            None,
        )

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
        if self.attr:
            return self.attr.name or ""
        return self.stereotype.name or ""

    @GObject.Property(type=bool, default=False)
    def applied(self):
        return bool(self.attr)

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

    @GObject.Property(type=bool, default=False)
    def value_editable(self):
        return bool(self.attr)

    @GObject.Property(type=GObject.TYPE_STRV)
    def indent_classes(self):
        return ["stereotype-value"] if self.attr else []

    @GObject.Property(type=str)
    def slot_value(self):
        return self.slot.value if self.slot else ""

    @slot_value.setter  # type: ignore[no-redef]
    @transactional
    def slot_value(self, value):
        if value:
            if self.slot is None:
                print("create slot")
                self.slot = UML.recipes.add_slot(self.instance, self.attr)
            print("set slot value")
            self.slot.value = value
        elif self.slot:
            del self.stereotype.slot[self.slot]
            self.slot = None


def stereotype_model(subject: Element):
    model = Gio.ListStore.new(StereotypeView.__gtype__)
    stereotypes = UML.recipes.get_stereotypes(subject)

    for st in stereotypes:
        model.append(StereotypeView(subject, st, None))

        for attr in all_attributes(st):
            model.append(StereotypeView(subject, st, attr))

    return model  # , (toggle_stereotype, subject, model), (set_value, model)


def all_attributes(stereotype, seen=None):
    if seen is None:
        seen = {stereotype}

    for super_type in stereotype.generalization[:].general[:]:
        if super_type not in seen:
            seen.add(super_type)
            yield from all_attributes(super_type)
    yield from (attr for attr in stereotype.ownedAttribute if not attr.association)


def name_list_item_factory(signal_handlers=None):
    ui_string = translated_ui_string("gaphor.UML.profiles", "stereotype-name-cell.ui")

    return Gtk.BuilderListItemFactory.new_from_bytes(
        Gtk.Builder.BuilderScope(signal_handlers),
        GLib.Bytes.new(ui_string.encode("utf-8")),
    )


def value_list_item_factory(signal_handlers=None):
    return list_item_factory(
        "text-field-cell.ui",
        klass=StereotypeView,
        attribute=StereotypeView.slot_value,
        placeholder_text=gettext("New Slot Value…"),
        signal_handlers=text_field_handlers("slot_value"),
    )
