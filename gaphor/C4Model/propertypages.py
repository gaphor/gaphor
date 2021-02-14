import importlib.resources

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
class ContainerPropertyPage(PropertyPageBase):

    order = 15

    def __init__(self, subject: c4model.C4Container):
        super().__init__()
        assert subject
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        builder = new_builder("container-editor", "description-text-buffer")
        subject = self.subject

        technology = builder.get_object("technology")
        technology.set_text(subject.technology or "")

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
                "technology-changed": (self._on_technology_changed,),
                "container-destroyed": (self.watcher.unsubscribe_all,),
            }
        )
        return builder.get_object("container-editor")

    @transactional
    def _on_technology_changed(self, entry):
        self.subject.technology = entry.get_text()

    @transactional
    def _on_description_changed(self, buffer):
        self.subject.description = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
