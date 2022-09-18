"""Stereotype property page."""
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.modeling.element import Element
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.UML.profiles.metaclasspropertypage import new_builder


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

        model, toggle_stereotype_handler, set_slot_value_handler = stereotype_model(
            subject
        )

        builder = new_builder(
            "stereotypes-editor",
            signals={
                "show-stereotypes-changed": (self._on_show_stereotypes_change,),
                "toggle-stereotype": toggle_stereotype_handler,
                "set-slot-value": set_slot_value_handler,
            },
        )

        show_stereotypes = builder.get_object("show-stereotypes")

        if hasattr(self.item, "show_stereotypes"):
            show_stereotypes.set_active(self.item.show_stereotypes)
        elif Gtk.get_major_version() == 3:
            show_stereotypes.destroy()
        else:
            show_stereotypes.unparent()

        stereotype_list = builder.get_object("stereotype-list")
        stereotype_list.set_model(model)

        return builder.get_object("stereotypes-editor")

    @transactional
    def _on_show_stereotypes_change(self, button, gparam):
        self.item.show_stereotypes = button.get_active()


def stereotype_model(subject):
    model = Gtk.TreeStore.new(
        [
            str,  # stereotype/attribute
            str,  # value
            bool,  # active / is applied stereotype
            bool,  # visible  checkbox (is stereotype)
            bool,  # value editable
            object,  # stereotype / attribute
            object,  # instance specification
            object,  # slot
        ]
    )
    refresh(subject, model)

    return model, (toggle_stereotype, subject, model), (set_value, model)


def refresh(subject: Element, model: Gtk.TreeStore):
    stereotypes = UML.recipes.get_stereotypes(subject)
    instances = subject.appliedStereotype

    def upsert(path, parent, row_data):
        try:
            new_row = model.get_iter(path)
        except ValueError:
            new_row = model.append(parent, row_data)
        else:
            row = model[path]
            row[:] = row_data
        return new_row

    for st_index, st in enumerate(stereotypes):
        applied = next(
            (applied for applied in instances if st in applied.classifier), None
        )

        parent = upsert(
            f"{st_index}",
            None,
            (st.name, "", bool(applied), True, False, st, None, None),
        )
        for attr_index, attr in enumerate(all_attributes(st)):
            slot = (
                next(
                    (slot for slot in applied.slot if slot.definingFeature is attr),
                    None,
                )
                if applied
                else None
            )
            value = slot.value if slot else ""
            upsert(
                f"{st_index}:{attr_index}",
                parent,
                (
                    attr.name,
                    value,
                    bool(applied),
                    False,
                    bool(applied),
                    attr,
                    applied,
                    slot,
                ),
            )


def all_attributes(stereotype, seen=None):
    if seen is None:
        seen = {stereotype}

    for super_type in stereotype.generalization[:].general[:]:
        if super_type not in seen:
            seen.add(super_type)
            yield from all_attributes(super_type)
    yield from (attr for attr in stereotype.ownedAttribute if not attr.association)


@transactional
def toggle_stereotype(renderer, path, subject, model):
    row = model[path]
    _, _, is_applied, _, _, stereotype, _, _ = row
    value = not is_applied

    if value:
        UML.recipes.apply_stereotype(subject, stereotype)
    else:
        UML.recipes.remove_stereotype(subject, stereotype)

    row[2] = value

    refresh(subject, model)


@transactional
def set_value(renderer, path, value, model):
    """Set value of stereotype property applied to an UML element."""
    row = model[path]
    _, _, _, _, _, attr, applied, slot = row
    if isinstance(attr, UML.Stereotype):
        return  # don't edit stereotype rows

    if slot is None:
        if value:
            slot = UML.recipes.add_slot(applied, attr)

        else:
            return  # nothing to do and don't create slot without value

    assert slot

    if value:
        slot.value = value
    else:
        # no value, then remove slot
        del applied.slot[slot]
        slot = None
        value = ""

    row[1] = value
    row[7] = slot
