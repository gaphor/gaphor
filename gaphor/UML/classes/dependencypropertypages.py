from gaphor import UML
from gaphor.core.modeling import Dependency
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML.classes.classespropertypages import new_builder
from gaphor.UML.classes.dependency import DependencyItem


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 20

    DEPENDENCIES = (
        Dependency,
        UML.Usage,
        UML.Realization,
        UML.InterfaceRealization,
    )

    def __init__(self, item, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager
        self.watcher = self.item.watcher()
        self.builder = new_builder(
            "dependency-editor",
            signals={
                "dependency-type-changed": (self._on_dependency_type_change,),
                "automatic-changed": (self._on_auto_dependency_change,),
            },
        )

    def construct(self):
        automatic = self.builder.get_object("automatic")
        automatic.set_active(self.item.auto_dependency)

        self.update()

        self.watcher.watch("subject", self._on_subject_change)

        return unsubscribe_all_on_destroy(
            self.builder.get_object("dependency-editor"), self.watcher
        )

    def _on_subject_change(self, event):
        self.update()

    def update(self):
        """Update dependency type combo box.

        Disallow dependency type when dependency is established.
        """
        dropdown = self.builder.get_object("dependency-dropdown")
        index = self.DEPENDENCIES.index(self.item.dependency_type)
        dropdown.props.sensitive = not self.item.auto_dependency
        dropdown.set_selected(index)

    def _on_dependency_type_change(self, dropdown, _pspec):
        cls = self.DEPENDENCIES[dropdown.get_selected()]
        with Transaction(self.event_manager):
            self.item.dependency_type = cls
            if subject := self.item.subject:
                UML.recipes.swap_element(subject, cls)
                self.item.request_update()

    def _on_auto_dependency_change(self, switch, gparam):
        with Transaction(self.event_manager):
            self.item.auto_dependency = switch.get_active()
            self.update()
