from gaphor import UML
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.classespropertypages import new_builder
from gaphor.UML.profiles.stereotypepropertypages import (
    stereotype_key_handler,
    stereotype_model,
    stereotype_set_model_with_interaction,
)


@PropertyPages.register(UML.Association)
class AssociationPropertyPage(PropertyPageBase):
    NAVIGABILITY = (None, False, True)
    AGGREGATION = UML.Property.aggregation.values

    order = 20

    def __init__(self, subject: UML.Association, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()
        self.end_name_change_semaphore = 0

    def construct_end(self, builder, end_name, subject):
        title = builder.get_object(f"{end_name}-title")
        if subject.type:
            title.set_text(f"Member End (: {subject.type.name})")

        self.update_end_name(builder, end_name, subject)

        navigation = builder.get_object(f"{end_name}-navigation")
        navigation.set_selected(self.NAVIGABILITY.index(subject.navigability))

        aggregation = builder.get_object(f"{end_name}-aggregation")
        aggregation.set_selected(self.AGGREGATION.index(subject.aggregation))

        if stereotypes_model := stereotype_model(subject, self.event_manager):
            stereotype_list = builder.get_object(f"{end_name}-stereotype-list")
            stereotype_set_model_with_interaction(stereotype_list, stereotypes_model)
        else:
            stereotype_frame = builder.get_object(f"{end_name}-stereotype-frame")
            stereotype_frame.set_visible(False)

    def update_end_name(self, builder, end_name, subject):
        name = builder.get_object(f"{end_name}-name")
        new_name = (
            format(
                subject,
                visibility=True,
                is_derived=True,
                multiplicity=True,
            )
            or ""
        )
        if not (name.is_focus() or self.end_name_change_semaphore):
            self.end_name_change_semaphore += 1
            name.set_text(new_name)
            self.end_name_change_semaphore -= 1
        return name

    def construct(self):
        if not self.subject or isinstance(self.subject, UML.Extension):
            return

        head_subject = self.subject.memberEnd[0]
        tail_subject = self.subject.memberEnd[1]

        builder = new_builder(
            "association-editor",
            "association-info",
            signals={
                "head-name-changed": (self._on_end_name_change, head_subject),
                "head-navigation-changed": (
                    self._on_end_navigability_change,
                    head_subject,
                ),
                "head-aggregation-changed": (
                    self._on_end_aggregation_change,
                    head_subject,
                ),
                "head-info-clicked": (self._on_association_info_clicked,),
                "head-stereotype-key-pressed": (stereotype_key_handler,),
                "tail-name-changed": (self._on_end_name_change, tail_subject),
                "tail-navigation-changed": (
                    self._on_end_navigability_change,
                    tail_subject,
                ),
                "tail-aggregation-changed": (
                    self._on_end_aggregation_change,
                    tail_subject,
                ),
                "tail-info-clicked": (self._on_association_info_clicked,),
                "tail-stereotype-key-pressed": (stereotype_key_handler,),
            },
        )

        self.info = builder.get_object("association-info")
        help_link(builder, "head-info-icon", "head-info")
        help_link(builder, "tail-info-icon", "tail-info")

        self.construct_end(builder, "head", head_subject)
        self.construct_end(builder, "tail", tail_subject)

        def name_handler(event):
            end_name = "head" if event.element is head_subject else "tail"
            self.update_end_name(builder, end_name, event.element)

        def restore_nav_handler(event):
            for end_name, end_subject in (
                ("head", head_subject),
                ("tail", tail_subject),
            ):
                combo = builder.get_object(f"{end_name}-navigation")
                self._on_end_navigability_change(combo, None, end_subject)

        # Watch on association end:
        if self.watcher:
            self.watcher.watch("memberEnd[Property].name", name_handler).watch(
                "memberEnd[Property].visibility", name_handler
            ).watch("memberEnd[Property].lowerValue", name_handler).watch(
                "memberEnd[Property].upperValue", name_handler
            ).watch(
                "memberEnd[Property].type",
                restore_nav_handler,
            )

        return unsubscribe_all_on_destroy(
            builder.get_object("association-editor"), self.watcher
        )

    def _on_end_name_change(self, entry, subject):
        if not self.end_name_change_semaphore:
            self.end_name_change_semaphore += 1
            with Transaction(self.event_manager):
                parse(subject, entry.get_text())
            self.end_name_change_semaphore -= 1

    def _on_end_navigability_change(self, dropdown, _pspec, subject):
        if subject and subject.opposite and subject.opposite.type:
            with Transaction(self.event_manager):
                UML.recipes.set_navigability(
                    subject.association,
                    subject,
                    self.NAVIGABILITY[dropdown.get_selected()],
                )

    def _on_end_aggregation_change(self, dropdown, _pspec, subject):
        with Transaction(self.event_manager):
            subject.aggregation = self.AGGREGATION[dropdown.get_selected()]

    def _on_association_info_clicked(self, widget, event):
        self.info.set_relative_to(widget)
        self.info.set_visible(True)


@PropertyPages.register(AssociationItem)
class AssociationDirectionPropertyPage(PropertyPageBase):
    order = 20

    def __init__(self, item: AssociationItem, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not self.item.subject:
            return None

        builder = new_builder(
            "association-direction-editor",
            signals={
                "show-direction-changed": (self._on_show_direction_change,),
                "invert-direction-changed": (self.on_invert_direction_change,),
            },
        )

        show_direction = builder.get_object("show-direction")
        show_direction.set_active(self.item.show_direction)

        return builder.get_object("association-direction-editor")

    def _on_show_direction_change(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_direction = button.get_active()

    def on_invert_direction_change(self, button):
        with Transaction(self.event_manager):
            self.item.invert_direction()
