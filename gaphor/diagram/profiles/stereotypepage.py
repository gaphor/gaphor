"""
Stereotype property page.
"""

from gi.repository import GObject, Gtk

from gaphor import UML
from gaphor.core import _, inject, transactional
from gaphor.diagram.diagramitem import StereotypeSupport
from gaphor.diagram.propertypages import PropertyPages, PropertyPageBase


def create_stereotype_tree_view(model, toggle_stereotype, set_slot_value):
    """
    Create a tree view for an editable tree model.

    :Parameters:
     model
        Model, for which tree view is created.
    """
    tree_view = Gtk.TreeView.new_with_model(model)

    # Stereotype/Attributes
    col = Gtk.TreeViewColumn.new()
    col.set_title("%s / %s" % (_("Stereotype"), _("Attribute")))
    col.set_expand(True)
    renderer = Gtk.CellRendererToggle()
    renderer.set_property("active", True)
    renderer.set_property("activatable", True)
    renderer.connect("toggled", toggle_stereotype, model, 2)
    col.pack_start(renderer, False)
    col.add_attribute(renderer, "active", 2)

    def show_checkbox(column, cell, model, iter, data):
        # value = model.get_value(iter, 4)
        # cell.set_property('active', value is not None)
        value = model.get_value(iter, 3)
        cell.set_property("visible", isinstance(value, UML.Stereotype))

    col.set_cell_data_func(renderer, show_checkbox)

    renderer = Gtk.CellRendererText.new()
    renderer.set_property("editable", False)
    renderer.set_property("is-expanded", True)
    col.pack_start(renderer, False)
    col.add_attribute(renderer, "text", 0)
    tree_view.append_column(col)

    # TODO: use col.set_cell_data_func(renderer, func, None) to toggle visibility
    # Value
    renderer = Gtk.CellRendererText()
    renderer.set_property("is-expanded", True)
    renderer.connect("edited", set_slot_value, model, 1)
    col = Gtk.TreeViewColumn(_("Value"), renderer, text=1)
    col.set_expand(True)

    def set_editable(column, cell, model, iter, data):
        value = model.get_value(iter, 4)
        cell.set_property("editable", bool(value))

    col.set_cell_data_func(renderer, set_editable)
    tree_view.append_column(col)

    # tree_view.connect('key_press_event', remove_on_keypress)
    # tree_view.connect('key_press_event', swap_on_keypress)

    return tree_view


@PropertyPages.register(UML.Element)
class StereotypePage(PropertyPageBase):

    order = 40
    name = "Stereotypes"

    element_factory = inject("element_factory")

    def __init__(self, item):
        self.item = item
        self.size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

    def construct(self):
        page = Gtk.VBox()
        subject = self.item.subject
        if subject is None:
            return None

        stereotypes = UML.model.get_stereotypes(subject)
        if not stereotypes:
            return None

        # show stereotypes attributes toggle
        if isinstance(self.item, StereotypeSupport):
            hbox = Gtk.HBox()
            label = Gtk.Label(label="")
            hbox.pack_start(label, False, True, 0)
            button = Gtk.CheckButton(label=_("Show stereotypes attributes"))
            button.set_active(self.item.show_stereotypes_attrs)
            button.connect("toggled", self._on_show_stereotypes_attrs_change)
            hbox.pack_start(button, True, True, 0)
            page.pack_start(hbox, False, True, 0)

        # stereotype attributes
        # self.model = StereotypeAttributes(self.item.subject)
        self.model = Gtk.TreeStore.new([str, str, bool, object, object, object])
        tree_view = create_stereotype_tree_view(
            self.model, self._toggle_stereotype, self._set_value
        )
        page.pack_start(tree_view, True, True, 0)

        page.show_all()

        self.refresh()
        return page

    @transactional
    def _on_show_stereotypes_attrs_change(self, button):
        self.item.show_stereotypes_attrs = button.get_active()
        self.item.request_update()

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

            parent = self.model.append(None, (st.name, "", bool(obj), st, None, None))

            if obj:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        slot = slots.get(attr)
                        value = slot.value if slot else ""
                        data = (attr.name, value, True, attr, obj, slot)
                        # print 'data', data
                        self.model.append(parent, data)
            else:
                for attr in st.ownedAttribute:
                    if not attr.association:
                        data = (attr.name, "", False, attr, None, None)
                        # print 'no data', data
                        self.model.append(parent, data)

    @transactional
    def _set_value(self, renderer, path, value, model, col=0):
        iter = model.get_iter(path)
        self.set_slot_value(iter, value)

    @transactional
    def _toggle_stereotype(self, renderer, path, model, col):
        iter = model.get_iter(path)
        self.select_stereotype(iter)

    def select_stereotype(self, iter):
        """
        Select the stereotype.
        """
        path = self.model.get_path(iter)
        row = self.model[path]
        name, old_value, is_applied, stereotype, _, _ = row
        value = not is_applied

        subject = self.item.subject
        if value:
            UML.model.apply_stereotype(subject, stereotype)
        else:
            UML.model.remove_stereotype(subject, stereotype)

        row[2] = value

        # TODO: change refresh in a refresh of the data model, rather than a clear-refresh
        self.refresh()

    def set_slot_value(self, iter, value):
        """
        Set value of stereotype property applied to an UML element.

        Slot is created if instance Create valuChange value of instance spe
        """
        path = self.model.get_path(iter)
        row = self.model[path]
        name, old_value, is_applied, attr, obj, slot = row
        if isinstance(attr, UML.Stereotype):
            return  # don't edit stereotype rows

        if slot is None and not value:
            return  # nothing to do and don't create slot without value

        if slot is None:
            slot = UML.model.add_slot(self.item.model, obj, attr)

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


# vim:sw=4:et:ai
