import importlib.resources

from gi.repository import Gtk

from gaphor.core import transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages
from gaphor.SysML import sysml


def new_builder(*object_ids):
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path("gaphor.SysML", "propertypages.glade") as glade_file:
        builder.add_objects_from_file(str(glade_file), object_ids)
    return builder


@PropertyPages.register(sysml.Requirement)
class RequirementPropertyPage(PropertyPageBase):

    order = 15

    def __init__(self, subject: sysml.Requirement):
        super().__init__()
        assert subject
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        builder = new_builder("requirement-editor", "requirement-text-buffer")
        subject = self.subject

        entry = builder.get_object("requirement-id")
        entry.set_text(subject.externalId or "")

        def id_handler(event):
            if event.element is subject and event.new_value is not None:
                entry.set_text(event.new_value)

        self.watcher.watch("name", id_handler)

        text_view = builder.get_object("requirement-text")

        buffer = builder.get_object("requirement-text-buffer")
        if subject.text:
            buffer.set_text(subject.text)

        changed_id = buffer.connect("changed", self._on_text_changed)

        def text_handler(event):
            if not text_view.props.has_focus:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)

        self.watcher.watch("text", text_handler).subscribe_all()

        builder.connect_signals(
            {
                "requirement-id-changed": (self._on_id_changed,),
                "requirement-destroyed": (self.watcher.unsubscribe_all,),
            }
        )
        return builder.get_object("requirement-editor")

    @transactional
    def _on_id_changed(self, entry):
        self.subject.externalId = entry.get_text()

    @transactional
    def _on_text_changed(self, buffer):
        self.subject.text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
