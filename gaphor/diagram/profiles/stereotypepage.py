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
        self.model.clear()
        subject = self.item.subject
        stereotypes = UML.model.get_stereotypes(subject)
        instances = subject.appliedStereotype

        # shortcut map stereotype -> slot (InstanceSpecification)
        slots = {}
        for obj in instances:
            for slot in obj.slot:
                slots[slot.definingFeature] = slot

        for st in stereotypes:
            for obj in instances:
                if st in obj.classifier:
                    break
            else:
                obj = None

            parent = self.model.append(
                None, (st.name, "", bool(obj), True, False, st, None, None)
            )

            if obj:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        slot = slots.get(attr)
                        value = slot.value if slot else ""
                        data = (attr.name, value, True, False, True, attr, obj, slot)
                        self.model.append(parent, data)
            else:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        data = (attr.name, "", False, False, True, attr, None, None)
                        self.model.append(parent, data)

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

        # TODO: change refresh in a refresh of the data model, rather than a clear-refresh
        self.refresh()

    @transactional
    def _set_value(self, renderer, path, value, model, col=0):
        """
        Set value of stereotype property applied to an UML element.

        Slot is created if instance Create valuChange value of instance spe
        """
        row = self.model[path]
        name, old_value, is_applied, _, _, attr, obj, slot = row
        if isinstance(attr, UML.Stereotype):
            return  # don't edit stereotype rows

        if slot is None and not value:
            return  # nothing to do and don't create slot without value

        if slot is None:
            slot = UML.model.add_slot(obj, attr)

        assert slot

        if value:
            slot.value = value
        else:
            # no value, then remove slot
            del obj.slot[slot]
            slot = None
            value = ""

        row[1] = value
        row[5] = slot
