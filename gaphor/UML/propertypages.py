from gi.repository import Gdk, Gio, GLib, Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    LabelValue,
    PropertyPageBase,
    new_resource_builder,
)
from gaphor.i18n import translated_ui_string

new_builder = new_resource_builder("gaphor.UML")


class TypedElementPropertyPage(PropertyPageBase):
    order = 31

    def __init__(self, item):
        assert (not item.subject) or isinstance(
            item.subject, UML.TypedElement
        ), item.subject
        super().__init__()
        self.item = item

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder(
            "typed-element-editor",
            signals={
                "show-type-changed": (self._on_show_type_change,),
            },
        )

        dropdown = builder.get_object("element-type")
        model = list_of_classifiers(self.item.subject.model, UML.Classifier)
        dropdown.set_model(model)

        if self.item.subject.type:
            dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(model)
                    if lv.value == self.item.subject.type.id
                )
            )

        dropdown.connect("notify::selected", self._on_property_type_changed)

        if hasattr(self.item, "show_type"):
            show_type = builder.get_object("show-type")
            show_type.set_active(self.item.show_type)
        else:
            builder.get_object("type-toggle-box").unparent()

        return builder.get_object("typed-element-editor")

    @transactional
    def _on_property_type_changed(self, dropdown, _pspec):
        subject = self.item.subject
        if id := dropdown.get_selected_item().value:
            element = subject.model.lookup(id)
            assert isinstance(element, UML.Type)
            subject.type = element
        else:
            del subject.type

    @transactional
    def _on_show_type_change(self, button, _gparam):
        self.item.show_type = button.get_active()


def list_of_classifiers(element_factory, required_type):
    model = Gio.ListStore.new(LabelValue)
    model.append(LabelValue("", None))
    for c in sorted(
        (c for c in element_factory.select(required_type) if c.name),
        key=lambda c: c.name or "",
    ):
        model.append(LabelValue(c.name, c.id))
    return model


def list_item_factory(
    ui_filename, klass, attribute, placeholder_text="", signal_handlers=None
):
    ui_string = translated_ui_string("gaphor.UML", ui_filename).format(
        gtype_name=klass.__gtype__.name,
        attribute=attribute.name,
        placeholder_text=placeholder_text,
    )

    return Gtk.BuilderListItemFactory.new_from_bytes(
        Gtk.Builder.BuilderScope(signal_handlers),
        GLib.Bytes.new(ui_string.encode("utf-8")),
    )


def create_list_store(type, elements, create_element):
    store = Gio.ListStore.new(type)

    for attr in elements:
        store.append(create_element(attr))

    store.append(create_element(None))

    return store


def update_list_store(
    store: Gio.ListStore, get_element, elements, create_element
) -> Gio.ListStore:
    n = 0
    for element in elements:
        if (item := store.get_item(n)) is not None and element is not get_element(item):
            store.remove(n)
            store.insert(n, create_element(element))
        n += 1

    while store.get_n_items() > n:
        store.remove(store.get_n_items() - 1)

    if (
        not store.get_n_items()
        or get_element(store.get_item(store.get_n_items() - 1)) is not None
    ):
        store.append(create_element(None))
    return store


def text_field_handlers(model_field: str):
    def on_double_click(ctrl, n_press, x, y):
        if n_press == 2:
            text = ctrl.get_widget()
            text.start_editing()

    def on_done_editing(list_item, should_commit):
        text = list_item.get_child()
        if should_commit:
            setattr(list_item.get_item(), model_field, text.editable_text)

    return {
        "on_double_click": on_double_click,
        "on_done_editing": on_done_editing,
    }


def check_button_handlers(model_field: str):
    def on_toggled(list_item):
        button = list_item.get_child()
        setattr(list_item.get_item(), model_field, button.get_active())

    return {
        "on_toggled": on_toggled,
    }


@transactional
def list_view_key_handler(ctrl, keyval, _keycode, state):
    """Handle keyboard shortcuts in a list view in the property editor.

    Attach to ``Gtk.EventControllerKey:key-pressed`` signals.
    """
    list_view = ctrl.get_widget()
    selection = list_view.get_model()
    item = selection.get_selected_item()

    if keyval in (Gdk.KEY_F2,):
        item.start_editing()
        return True

    if not item or item.empty():
        return False

    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace) and not state & (
        Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
    ):
        item.unlink()
        return True

    elif keyval in (Gdk.KEY_equal, Gdk.KEY_plus, Gdk.KEY_minus, Gdk.KEY_underscore):
        pos = selection.get_selected()
        swap_pos = pos + 1 if keyval in (Gdk.KEY_equal, Gdk.KEY_plus) else pos - 1
        if not 0 <= swap_pos < selection.get_n_items():
            return False

        other = selection.get_item(swap_pos)
        if not other or other.empty():
            return False

        if item.swap(item, other):
            selection.set_selected(swap_pos)
        return True

    return False
