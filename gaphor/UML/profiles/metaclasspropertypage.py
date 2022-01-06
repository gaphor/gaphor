from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    combo_box_text_auto_complete,
    new_resource_builder,
)

new_builder = new_resource_builder("gaphor.UML.profiles")


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
            (c, c)
            for c in dir(UML)
            if _issubclass(getattr(UML, c), UML.Element) and c != "Stereotype"
        )
    )

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        if not UML.recipes.is_metaclass(self.subject):
            return

        builder = new_builder(
            "metaclass-editor",
            signals={
                "metaclass-combo-changed": (self._on_name_changed,),
                "metaclass-combo-destroy": (self.watcher.unsubscribe_all,),
            },
        )

        combo = builder.get_object("metaclass-combo")
        combo_box_text_auto_complete(
            combo, self.CLASSES, self.subject and self.subject.name or ""
        )

        entry = combo.get_child()

        def handler(event):
            if event.element is self.subject and entry.get_text() != event.new_value:
                entry.set_text(event.new_value or "")

        self.watcher.watch("name", handler)

        return builder.get_object("metaclass-editor")

    @transactional
    def _on_name_changed(self, combo):
        self.subject.name = combo.get_active_text()
