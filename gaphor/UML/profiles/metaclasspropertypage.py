from gi.repository import Gtk

from gaphor import UML
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction

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

    CLASSES = sorted(
        c
        for c in dir(UML)
        if _issubclass(getattr(UML, c), UML.Element) and c != "Stereotype"
    )

    def __init__(self, subject: UML.Class, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject.watcher()

    def construct(self):
        if not UML.recipes.is_metaclass(self.subject):
            return

        builder = new_builder(
            "metaclass-editor",
        )

        dropdown = builder.get_object("metaclass-dropdown")
        dropdown.set_model(Gtk.StringList.new(self.CLASSES))
        if self.subject and self.subject.name in self.CLASSES:
            dropdown.set_selected(self.CLASSES.index(self.subject.name))

        @handler_blocking(dropdown, "notify::selected-item", self._on_name_changed)
        def handler(event):
            if event.element is self.subject and event.new_value in self.CLASSES:
                dropdown.set_selected(self.CLASSES.index(self.subject.name))

        self.watcher.watch("name", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("metaclass-editor"), self.watcher
        )

    def _on_name_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            self.subject.name = dropdown.get_selected_item().get_string()
