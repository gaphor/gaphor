import importlib.resources
from typing import Union

from gi.repository import Gtk

from gaphor.C4Model import c4model
from gaphor.core import transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages


def new_builder(*object_ids):
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path(
        "gaphor.C4Model", "propertypages.glade"
    ) as glade_file:
        builder.add_objects_from_file(str(glade_file), object_ids)
    return builder


@PropertyPages.register(c4model.C4Container)
@PropertyPages.register(c4model.C4Person)
class DescriptionPropertyPage(PropertyPageBase):

    order = 14

    def __init__(self, subject: Union[c4model.C4Container, c4model.C4Person]):
        super().__init__()
        assert subject
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        builder = new_builder("description-editor", "description-text-buffer")
        subject = self.subject

        description = builder.get_object("description")

        buffer = builder.get_object("description-text-buffer")
        if subject.description:
            buffer.set_text(subject.description)

        changed_id = buffer.connect("changed", self._on_description_changed)

        def text_handler(event):
            if not description.props.has_focus:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)

        self.watcher.watch("description", text_handler)

        builder.connect_signals(
            {
                "container-destroyed": (self.watcher.unsubscribe_all,),
            }
        )
        return builder.get_object("description-editor")

    @transactional
    def _on_description_changed(self, buffer):
        self.subject.description = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )


@PropertyPages.register(c4model.C4Container)
class TechnologyPropertyPage(PropertyPageBase):

    order = 15

    def __init__(self, subject: c4model.C4Container):
        super().__init__()
        assert subject
        self.subject = subject

    def construct(self):
        builder = new_builder("technology-editor")
        subject = self.subject

        technology = builder.get_object("technology")
        technology.set_text(subject.technology or "")

        builder.connect_signals(
            {
                "technology-changed": (self._on_technology_changed,),
            }
        )
        return builder.get_object("technology-editor")

    @transactional
    def _on_technology_changed(self, entry):
        self.subject.technology = entry.get_text()
