from gi.repository import Gtk

from gaphor import UML
from gaphor.core.format import format
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    on_text_cell_edited,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import transactional
from gaphor.UML.classes.classespropertypages import (
    AttributesPage,
    ClassEnumerationLiterals,
    OperationsPage,
    new_resource_builder,
    on_keypress_event,
)
from gaphor.UML.classes.enumeration import EnumerationItem

new_builder = new_resource_builder("gaphor.UML.classes")


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

        self.model = ClassEnumerationLiterals(self.item)

        builder = new_builder(
            "enumerations-editor",
            "enumerations-info",
            signals={
                "show-enumerations-changed": (self._on_show_enumerations_change,),
                "enumerations-name-edited": (on_text_cell_edited, self.model, 0),
                "enumerations-info-clicked": (self.on_enumerations_info_clicked),
            },
        )

        self.info = builder.get_object("enumerations-info")
        help_link(builder, "enumerations-info-icon", "enumerations-info")

        show_enumerations = builder.get_object("show-enumerations")
        show_enumerations.set_active(self.item.show_enumerations)

        tree_view: Gtk.TreeView = builder.get_object("enumerations-list")
        tree_view.set_model(self.model)

        controller = Gtk.EventControllerKey.new()
        tree_view.add_controller(controller)

        controller.connect("key-pressed", on_keypress_event, tree_view)

        def handler(event):
            enumeration = event.element
            for row in self.model:
                if row[-1] is enumeration:
                    row[:] = [format(enumeration), enumeration]

        self.watcher.watch("ownedLiteral.name", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("enumerations-editor"), self.watcher
        )

    @transactional
    def _on_show_enumerations_change(self, button, gparam):
        self.item.show_enumerations = button.get_active()
        self.item.request_update()

    def on_enumerations_info_clicked(self, image, event):
        self.info.show()


PropertyPages.register(EnumerationItem)(AttributesPage)
PropertyPages.register(EnumerationItem)(OperationsPage)
