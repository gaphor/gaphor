from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder


def _issubclass(c, b):
    try:
        return issubclass(c, b)
    except TypeError:
        return False


@PropertyPages.register(UML.Class)
class MetaclassPropertyPage(PropertyPageBase):
    """Adapter which shows a property page for a class view.
    Also handles metaclasses.
    """

    order = 10

    subject: UML.Class

    CLASSES = list(
        sorted(
            c
            for c in dir(UML)
            if _issubclass(getattr(UML, c), UML.Element) and c != "Stereotype"
        )
    )

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        if not UML.model.is_metaclass(self.subject):
            return

        builder = new_builder("metaclass-editor")

        combo = builder.get_object("metaclass-combo")
        for c in self.CLASSES:
            combo.append_text(c)

        completion = Gtk.EntryCompletion()
        completion.set_model(combo.get_model())
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)

        entry = combo.get_child()
        entry.set_completion(completion)

        entry.set_text(self.subject and self.subject.name or "")

        def handler(event):
            if event.element is self.subject and event.new_value is not None:
                entry.set_text(event.new_value)

        self.watcher.watch("name", handler).subscribe_all()

        builder.connect_signals(
            {
                "metaclass-combo-changed": (self._on_name_changed,),
                "metaclass-combo-destroy": (self.watcher.unsubscribe_all,),
            }
        )

        return builder.get_object("metaclass-editor")

    @transactional
    def _on_name_changed(self, combo):
        self.subject.name = combo.get_active_text()
