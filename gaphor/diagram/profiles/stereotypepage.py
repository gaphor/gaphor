"""
Stereotype property page.
"""

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, builder


@PropertyPages.register(UML.Element)
class StereotypePage(PropertyPageBase):

    order = 40
    name = "Stereotypes"

    def __init__(self, item):
        self.item = item
        self.builder = builder("stereotypes-editor")

    def construct(self):

        subject = self.item.subject
        if not subject:
            return None

        stereotypes = UML.model.get_stereotypes(subject)
        if not stereotypes:
            return None

        page = self.builder.get_object("stereotypes-editor")

        show_stereotypes = self.builder.get_object("show-stereotypes")
        show_stereotypes.set_sensitive(hasattr(self.item, "show_stereotypes"))
        # show stereotypes attributes toggle
        if hasattr(self.item, "show_stereotypes"):
            show_stereotypes.set_active(self.item.show_stereotypes)

        self.model = Gtk.TreeStore.new(
            [
                str,  # stereotype/attribute
                str,  # value
                bool,  # is applied stereotype
                bool,  # show checkbox (is stereotype)
                bool,  # value editable
                object,  # stereotype / attribute
                object,  # value editable
                object,  # slot element
            ]
        )

        stereotype_list = self.builder.get_object("stereotype-list")
        stereotype_list.set_model(self.model)

        self.builder.connect_signals(
            {
                "show-stereotypes-changed": (self._on_show_stereotypes_change,),
                "toggle-stereotype": (self._toggle_stereotype, self.model, 2),
                "set-slot-value": (self._set_value, self.model, 1),
            }
        )
        self.refresh()
        return page

    def refresh(self):
        subject = self.item.subject
        stereotypes = UML.model.get_stereotypes(subject)
        instances = subject.appliedStereotype

        def upsert(path, parent, row_data):
            try:
                new_row = self.model.get_iter(path)
            except ValueError:
                new_row = self.model.append(parent, row_data)
            else:
                row = self.model[path]
                row[:] = row_data
            return new_row

        # shortcut map stereotype -> slot (InstanceSpecification)
        slots = {}
        for applied in instances:
            for slot in applied.slot:
                slots[slot.definingFeature] = slot

        for st_index, st in enumerate(stereotypes):
            for applied in instances:
                if st in applied.classifier:
                    break
            else:
                applied = None

            parent = upsert(
                f"{st_index}",
                None,
                (st.name, "", bool(applied), True, False, st, None, None),
            )
            for attr_index, attr in enumerate(
                attr for attr in st.ownedAttribute if not attr.association
            ):
                slot = slots.get(attr)
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

    @transactional
    def _on_show_stereotypes_change(self, button):
        self.item.show_stereotypes = button.get_active()

    @transactional
    def _toggle_stereotype(self, renderer, path, model, col):
        row = self.model[path]
        name, old_value, is_applied, _, _, stereotype, _, _ = row
        value = not is_applied

        subject = self.item.subject
        if value:
            UML.model.apply_stereotype(subject, stereotype)
        else:
            UML.model.remove_stereotype(subject, stereotype)

        row[2] = value

        self.refresh()

    @transactional
    def _set_value(self, renderer, path, value, model, col=0):
        """
        Set value of stereotype property applied to an UML element.

        Slot is created if instance Create valuChange value of instance spe
        """
        row = self.model[path]
        name, old_value, is_applied, _, _, attr, applied, slot = row
        if isinstance(attr, UML.Stereotype):
            return  # don't edit stereotype rows

        if slot is None and not value:
            return  # nothing to do and don't create slot without value

        if slot is None:
            slot = UML.model.add_slot(applied, attr)

        assert slot

        if value:
            slot.value = value
        else:
            # no value, then remove slot
            del applied.slot[slot]
            slot = None
            value = ""

        row[1] = value
        row[5] = slot
