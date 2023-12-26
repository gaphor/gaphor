"""Stereotype property page."""
from gi.repository import Gio, GObject, Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.core.modeling.element import Element
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
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
                list_item_factory(
                    "text-field-cell.ui",
                    klass=StereotypeView,
                    attribute=StereotypeView.name,
                    signal_handlers=text_field_handlers("name"),
                ),
                list_item_factory(
                    "text-field-cell.ui",
                    klass=StereotypeView,
                    attribute=StereotypeView.slot_value,
                    placeholder_text=gettext("New Slot Value…"),
                    signal_handlers=text_field_handlers("slot_value"),
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
        stereotype: UML.Stereotype | None,
        attr: UML.Property | None,
        slot: UML.Slot | None,
    ):
        super().__init__()
        self.stereotype = stereotype
        self.target = target
        self.attr = attr
        self.slot = slot

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

    @GObject.Property(type=str, default="")
    def name(self):
        if self.attr:
            return self.attr.name or ""
        if self.stereotype:
            return self.stereotype.name or ""
        return ""

    @GObject.Property(type=bool, default=False)
    def applied(self):
        instances = self.target.appliedStereotype
        st = self.stereotype
        if not st:
            return False
        return any(applied for applied in instances if st in applied.classifier)

    @applied.setter  # type: ignore[no-redef]
    @transactional
    def applied(self, value):
        if value and not self.instance:
            self.instance = UML.recipes.apply_stereotype(self.target, self.stereotype)
        elif self.instance:
            self.instance = UML.recipes.remove_stereotype(self.target, self.stereotype)

    @GObject.Property(type=bool, default=False)
    def checkbox_visible(self):
        return not bool(self.attr)

    @GObject.Property(type=bool, default=False)
    def value_editable(self):
        return bool(self.attr)

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
    instances = subject.appliedStereotype

    for st in stereotypes:
        model.append(StereotypeView(subject, st, None, None))

        # TODO: Add values/instance spec sub entries

        applied = next(
            (applied for applied in instances if st in applied.classifier), None
        )
        for attr in all_attributes(st):
            slot = (
                next(
                    (slot for slot in applied.slot if slot.definingFeature is attr),
                    None,
                )
                if applied
                else None
            )
            model.append(StereotypeView(subject, st, attr, slot))

    return model  # , (toggle_stereotype, subject, model), (set_value, model)


def all_attributes(stereotype, seen=None):
    if seen is None:
        seen = {stereotype}

    for super_type in stereotype.generalization[:].general[:]:
        if super_type not in seen:
            seen.add(super_type)
            yield from all_attributes(super_type)
    yield from (attr for attr in stereotype.ownedAttribute if not attr.association)
