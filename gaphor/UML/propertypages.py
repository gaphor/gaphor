from gi.repository import Gio

from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    LabelValue,
    PropertyPageBase,
    new_resource_builder,
)
from gaphor import UML


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
