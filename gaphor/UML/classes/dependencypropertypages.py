from gaphor import UML
from gaphor.diagram.propertypages import ComboModel, PropertyPageBase, PropertyPages
from gaphor.i18n import gettext
from gaphor.transaction import transactional
from gaphor.UML.classes.classespropertypages import new_builder
from gaphor.UML.classes.dependency import DependencyItem


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 20

    DEPENDENCY_TYPES = (
        (gettext("Dependency"), UML.Dependency),
        (gettext("Usage"), UML.Usage),
        (gettext("Realization"), UML.Realization),
        (gettext("Implementation"), UML.InterfaceRealization),
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
                "dependency-type-destroy": (self.watcher.unsubscribe_all,),
            },
        )

    def construct(self):
        dependency_combo = self.builder.get_object("dependency-combo")
        model = ComboModel(self.DEPENDENCY_TYPES)
        dependency_combo.set_model(model)

        automatic = self.builder.get_object("automatic")
        automatic.set_active(self.item.auto_dependency)

        self.update()

        self.watcher.watch("subject", self._on_subject_change)

        return self.builder.get_object("dependency-editor")

    def _on_subject_change(self, event):
        self.update()

    def update(self):
        """Update dependency type combo box.

        Disallow dependency type when dependency is established.
        """
        combo = self.builder.get_object("dependency-combo")
        if combo.get_model():
            item = self.item
            index = combo.get_model().get_index(item.dependency_type)
            combo.props.sensitive = not item.auto_dependency
            combo.set_active(index)

    @transactional
    def _on_dependency_type_change(self, combo):
        cls = combo.get_model().get_value(combo.get_active())
        self.item.dependency_type = cls
        subject = self.item.subject
        if subject:
            UML.recipes.swap_element(subject, cls)
            self.item.request_update()

    @transactional
    def _on_auto_dependency_change(self, switch, gparam):
        self.item.auto_dependency = switch.get_active()
        self.update()
