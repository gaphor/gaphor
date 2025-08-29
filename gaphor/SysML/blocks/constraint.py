from __future__ import annotations

from gi.repository import Gio, Gtk

from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.group import group
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    Text,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Constraint
from gaphor.UML.classes.classespropertypages import AttributeView
from gaphor.UML.classes.klass import attribute_watches
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment
from gaphor.UML.propertypages import (
    check_button_handlers,
    create_list_store,
    list_item_factory,
    list_view_activated,
    list_view_key_handler,
    text_field_handlers,
    update_list_store,
)
from gaphor.UML.recipes import get_applied_stereotypes
from gaphor.UML.uml import Namespace
from gaphor.UML.umlfmt import format_property


@represents(Constraint)
class ConstraintItem(Classified, ElementPresentation[Constraint]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("subject", self.on_subject_change)
        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_parameters", self.update_shapes
        ).watch("subject[UML:NamedElement].name").watch(
            "subject[UML:NamedElement].namespace.name"
        ).watch("subject[UML:Classifier].isAbstract", self.update_shapes)
        attribute_watches(self, "Constraint")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_parameters: attribute[int] = attribute("show_parameters", int, default=True)

    def on_subject_change(self, event):
        """If a constraint is created on a diagram, it is owned by the
        diagram's owner."""
        owner = self.diagram and getattr(self.diagram, "element", None)
        if (
            self.subject
            and owner
            and isinstance(owner, Namespace)
            and self.subject.owner is not owner
        ):
            # New items created from the toolbox do not have an owner yet.
            if not self.subject.owner:
                group(owner, self.subject)
        self.update_shapes()

    def additional_stereotypes(self):
        # Check if any other stereotypes are applied to avoid showing "constraintblock" redundantly
        if self.subject and not any(get_applied_stereotypes(self.subject)):
            return [self.diagram.gettext("constraint")]
        return ()

    def parameters_compartment(self):
        # Filter properties to only show those that are constraint parameters
        # (i.e., not typed by Constraint)
        if not self.subject:
            return Box()

        def lazy_format(attribute):
            return lambda: format_property(attribute) or self.diagram.gettext("unnamed")

        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=self.diagram.gettext("parameters")),
                ),
                *(
                    CssNode("attribute", attribute, Text(text=lazy_format(attribute)))
                    for attribute in self.subject.ownedAttribute
                    if not (attribute.type and isinstance(attribute.type, Constraint))
                ),
                draw=draw_top_separator,
            ),
        )

    def constraints_compartment(self):
        if not self.subject:
            return Box()
        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=self.diagram.gettext("constraints")),
                ),
                CssNode(
                    "constraint",
                    self.subject,
                    Text(
                        text=lambda: self.subject.specification
                        or self.diagram.gettext("«expression»")
                    ),
                ),
                draw=draw_top_separator,
            ),
        )

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(self, self.additional_stereotypes),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            self.constraints_compartment(),
            *(self.show_parameters and [self.parameters_compartment()] or []),
            draw=draw_border,
        )


def parameter_model(klass: Constraint, event_manager) -> Gio.ListStore:
    return create_list_store(
        AttributeView,
        (
            a
            for a in klass.ownedAttribute
            if not (a.type and isinstance(a.type, Constraint)) and not a.association
        ),
        lambda attr: AttributeView(attr, klass, event_manager),
    )


def update_parameter_model(
    store: Gio.ListStore, klass: Constraint, event_manager
) -> None:
    update_list_store(
        store,
        lambda item: item.attr,
        (
            a
            for a in klass.ownedAttribute
            if not (a.type and isinstance(a.type, Constraint)) and not a.association
        ),
        lambda attr: AttributeView(attr, klass, event_manager),
    )


@PropertyPages.register(Constraint)
class ConstraintParametersPage(PropertyPageBase):
    order = 20

    def __init__(self, subject, event_manager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        builder = new_resource_builder("gaphor.UML.classes")(
            "attributes-editor",
            signals={
                "attributes-activated": (list_view_activated,),
                "attributes-key-pressed": (list_view_key_handler,),
            },
        )

        column_view: Gtk.ColumnView = builder.get_object("attributes-list")

        for column, factory in zip(
            column_view.get_columns(),
            [
                list_item_factory(
                    "text-field-cell.ui",
                    klass=AttributeView,
                    attribute=AttributeView.attribute,
                    placeholder_text=gettext("New Parameter…"),
                    signal_handlers=text_field_handlers("attribute"),
                ),
                list_item_factory(
                    "check-button-cell.ui",
                    klass=AttributeView,
                    attribute=AttributeView.read_only,
                    signal_handlers=check_button_handlers("read_only"),
                ),
                list_item_factory(
                    "check-button-cell.ui",
                    klass=AttributeView,
                    attribute=AttributeView.static,
                    signal_handlers=check_button_handlers("static"),
                ),
            ],
            strict=False,
        ):
            column.set_factory(factory)

        self.model = parameter_model(self.subject, self.event_manager)
        selection = Gtk.SingleSelection.new(self.model)
        column_view.set_model(selection)

        if self.watcher:
            self.watcher.watch("ownedAttribute", self.on_parameters_changed)

        return builder.get_object("attributes-editor")

    def on_parameters_changed(self, event):
        update_parameter_model(self.model, self.subject, self.event_manager)
