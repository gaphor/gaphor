from gaphor import UML
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import transactional
from gaphor.UML.classes.classespropertypages import new_builder
from gaphor.UML.classes.dependency import DependencyItem


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 20

    DEPENDENCIES = (
        UML.Dependency,
        UML.Usage,
        UML.Realization,
        UML.InterfaceRealization,
    )

    def __init__(self, item):
        super().__init__()
        self.item = item
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

    @transactional
    def _on_dependency_type_change(self, dropdown, _pspec):
        cls = self.DEPENDENCIES[dropdown.get_selected()]
        self.item.dependency_type = cls
        if subject := self.item.subject:
            UML.recipes.swap_element(subject, cls)
            self.item.request_update()

    @transactional
    def _on_auto_dependency_change(self, switch, gparam):
        self.item.auto_dependency = switch.get_active()
        self.update()
