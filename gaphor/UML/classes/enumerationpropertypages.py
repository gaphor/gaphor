from gi.repository import Gtk

from gaphor import UML
from gaphor.core.format import format
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    on_text_cell_edited,
)
from gaphor.transaction import transactional
from gaphor.UML.classes import EnumerationItem
from gaphor.UML.classes.classespropertypages import (
    AttributesPage,
    ClassEnumerationLiterals,
    OperationsPage,
    new_builder,
    on_keypress_event,
)


@PropertyPages.register(EnumerationItem)
class EnumerationPage(PropertyPageBase):
    """An editor for enumeration literals for an enumeration."""

    order = 20

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        if not isinstance(self.item.subject, UML.Enumeration):
            return

        builder = new_builder("enumerations-editor")
        page = builder.get_object("enumerations-editor")

        show_enumerations = builder.get_object("show-enumerations")
        show_enumerations.set_active(self.item.show_enumerations)

        self.model = ClassEnumerationLiterals(self.item)

        tree_view: Gtk.TreeView = builder.get_object("enumerations-list")
        tree_view.set_model(self.model)

        def handler(event):
            enumeration = event.element
            for row in self.model:
                if row[-1] is enumeration:
                    row[:] = [format(enumeration), enumeration]

        self.watcher.watch("ownedLiteral.name", handler)

        builder.connect_signals(
            {
                "show-enumerations-changed": (self._on_show_enumerations_change,),
                "enumerations-name-edited": (on_text_cell_edited, self.model, 0),
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
                "enumerations-keypress": (on_keypress_event,),
            }
        )
        return page

    @transactional
    def _on_show_enumerations_change(self, button, gparam):
        self.item.show_attributes = button.get_active()
        self.item.request_update()


PropertyPages.register(EnumerationItem)(AttributesPage)
PropertyPages.register(EnumerationItem)(OperationsPage)
