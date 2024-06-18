from typing import Union

from gaphor.C4Model import c4model
from gaphor.core import Transaction
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)

new_builder = new_resource_builder("gaphor.C4Model")


@PropertyPages.register(c4model.C4Container)
@PropertyPages.register(c4model.C4Person)
class DescriptionPropertyPage(PropertyPageBase):
    order = 14

    def __init__(
        self, subject: Union[c4model.C4Container, c4model.C4Person], event_manager
    ):
        super().__init__()
        assert subject
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject.watcher()

    def construct(self):
        builder = new_builder(
            "description-editor",
            "description-text-buffer",
        )
        subject = self.subject

        description = builder.get_object("description")

        buffer = builder.get_object("description-text-buffer")
        if subject.description:
            buffer.set_text(subject.description)

        @handler_blocking(buffer, "changed", self._on_description_changed)
        def text_handler(event):
            if not description.props.has_focus:
                buffer.set_text(event.new_value)

        self.watcher.watch("description", text_handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("description-editor"), self.watcher
        )

    def _on_description_changed(self, buffer):
        with Transaction(self.event_manager):
            self.subject.description = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), False
            )


@PropertyPages.register(c4model.C4Container)
class TechnologyPropertyPage(PropertyPageBase):
    order = 15

    def __init__(self, subject: c4model.C4Container, event_manager):
        super().__init__()
        assert subject
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder(
            "technology-editor",
            signals={
                "technology-changed": (self._on_technology_changed,),
            },
        )
        subject = self.subject

        technology = builder.get_object("technology")
        technology.set_text(subject.technology or "")

        return builder.get_object("technology-editor")

    def _on_technology_changed(self, entry):
        with Transaction(self.event_manager):
            self.subject.technology = entry.get_text()
