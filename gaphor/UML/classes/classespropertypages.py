import logging

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.core.modeling import NamedElement
from gaphor.diagram.propertypages import (
    ComboModel,
    EditableTreeModel,
    PropertyPageBase,
    PropertyPages,
    new_builder,
    on_bool_cell_edited,
    on_keypress_event,
    on_text_cell_edited,
)
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.components.connector import ConnectorItem
from gaphor.UML.profiles.stereotypepropertypages import stereotype_model

log = logging.getLogger(__name__)


class ClassAttributes(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def _get_rows(self):
        for attr in self._item.subject.ownedAttribute:
            if not attr.association:
                yield [UML.format(attr), attr.isStatic, attr]

    def _create_object(self):
        attr = self._item.model.create(UML.Property)
        self._item.subject.ownedAttribute = attr
        return attr

    @transactional
    def _set_object_value(self, row, col, value):
        attr = row[-1]
        if col == 0:
            UML.parse(attr, value)
            row[0] = UML.format(attr)
        elif col == 1:
            attr.isStatic = not attr.isStatic
            row[1] = attr.isStatic
        elif col == 2:
            # Value in attribute object changed:
            row[0] = UML.format(attr)
            row[1] = attr.isStatic

    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedAttribute.swap(o1, o2)


class ClassOperations(EditableTreeModel):
    """GTK tree model to edit class operations."""

    def _get_rows(self):
        for operation in self._item.subject.ownedOperation:
            yield [
                UML.format(operation),
                operation.isAbstract,
                operation.isStatic,
                operation,
            ]

    def _create_object(self):
        operation = self._item.model.create(UML.Operation)
        self._item.subject.ownedOperation = operation
        return operation

    @transactional
    def _set_object_value(self, row, col, value):
        operation = row[-1]
        if col == 0:
            UML.parse(operation, value)
            row[0] = UML.format(operation)
        elif col == 1:
            operation.isAbstract = not operation.isAbstract
            row[1] = operation.isAbstract
        elif col == 2:
            operation.isStatic = not operation.isStatic
            row[2] = operation.isStatic
        elif col == 3:
            row[0] = UML.format(operation)
            row[1] = operation.isAbstract
            row[2] = operation.isStatic

    def _swap_objects(self, o1, o2):
        return self._item.subject.ownedOperation.swap(o1, o2)


@PropertyPages.register(NamedElement)
class NamedElementPropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject: NamedElement):
        super().__init__()
        assert subject is None or isinstance(subject, NamedElement), "%s" % type(
            subject
        )
        self.subject = subject
        self.watcher = subject.watcher() if subject else None

    def construct(self):
        if UML.model.is_metaclass(self.subject):
            return

        builder = new_builder("named-element-editor")

        subject = self.subject
        if not subject:
            return

        assert self.watcher

        entry = builder.get_object("name-entry")
        entry.set_text(subject and subject.name or "")

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.set_text(event.new_value)

        self.watcher.watch("name", handler).subscribe_all()

        builder.connect_signals(
            {
                "name-changed": (self._on_name_changed,),
                "name-entry-destroyed": (self.watcher.unsubscribe_all,),
            }
        )
        return builder.get_object("named-element-editor")

    @transactional
    def _on_name_changed(self, entry):
        self.subject.name = entry.get_text()


@PropertyPages.register(UML.Classifier)
class ClassifierPropertyPage(PropertyPageBase):

    order = 15

    def __init__(self, subject):
        self.subject = subject

    def construct(self):
        if UML.model.is_metaclass(self.subject):
            return

        builder = new_builder("classifier-editor")

        abstract = builder.get_object("abstract")
        abstract.set_active(self.subject.isAbstract)

        builder.connect_signals({"abstract-changed": (self._on_abstract_change,)})

        return builder.get_object("classifier-editor")

    @transactional
    def _on_abstract_change(self, button, gparam):
        self.subject.isAbstract = button.get_active()


@PropertyPages.register(InterfaceItem)
class InterfacePropertyPage(PropertyPageBase):
    """Adapter which shows a property page for an interface view."""

    order = 15

    def __init__(self, item):
        self.item = item

    def construct(self):
        builder = new_builder("interface-editor")
        item = self.item

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        disallowed = (ConnectorItem,)
        can_fold = not any(map(lambda i: isinstance(i, disallowed), connected_items))

        folded = builder.get_object("folded")
        folded.set_active(item.folded != Folded.NONE)
        folded.set_sensitive(can_fold)

        builder.connect_signals({"folded-changed": (self._on_fold_change,)})

        return builder.get_object("interface-editor")

    @transactional
    def _on_fold_change(self, button, gparam):
        item = self.item

        fold = button.get_active()

        item.folded = Folded.PROVIDED if fold else Folded.NONE


@PropertyPages.register(ClassItem)
@PropertyPages.register(InterfaceItem)
class AttributesPage(PropertyPageBase):
    """An editor for attributes associated with classes and interfaces."""

    order = 20

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder("attributes-editor")
        page = builder.get_object("attributes-editor")

        show_attributes = builder.get_object("show-attributes")
        show_attributes.set_active(self.item.show_attributes)

        self.model = ClassAttributes(self.item, (str, bool, object))

        tree_view: Gtk.TreeView = builder.get_object("attributes-list")
        tree_view.set_model(self.model)

        def handler(event):
            attribute = event.element
            for row in self.model:
                if row[-1] is attribute:
                    row[:] = [UML.format(attribute), attribute.isStatic, attribute]

        self.watcher.watch("ownedAttribute.name", handler).watch(
            "ownedAttribute.isDerived", handler
        ).watch("ownedAttribute.visibility", handler).watch(
            "ownedAttribute.isStatic", handler
        ).watch(
            "ownedAttribute.lowerValue", handler
        ).watch(
            "ownedAttribute.upperValue", handler
        ).watch(
            "ownedAttribute.defaultValue", handler
        ).watch(
            "ownedAttribute.typeValue", handler
        ).subscribe_all()

        builder.connect_signals(
            {
                "show-attributes-changed": (self._on_show_attributes_change,),
                "attributes-name-edited": (on_text_cell_edited, self.model, 0),
                "attributes-static-edited": (on_bool_cell_edited, self.model, 1),
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
                "attributes-keypress": (on_keypress_event,),
            }
        )
        return page

    @transactional
    def _on_show_attributes_change(self, button, gparam):
        self.item.show_attributes = button.get_active()
        self.item.request_update()


@PropertyPages.register(ClassItem)
@PropertyPages.register(InterfaceItem)
class OperationsPage(PropertyPageBase):
    """An editor for operations associated with classes and interfaces."""

    order = 30

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder("operations-editor")

        show_operations = builder.get_object("show-operations")
        show_operations.set_active(self.item.show_operations)

        self.model = ClassOperations(self.item, (str, bool, bool, object))

        tree_view: Gtk.TreeView = builder.get_object("operations-list")
        tree_view.set_model(self.model)

        def handler(event):
            operation = event.element
            for row in self.model:
                if row[-1] is operation:
                    row[:] = [
                        UML.format(operation),
                        operation.isAbstract,
                        operation.isStatic,
                        operation,
                    ]

        self.watcher.watch("ownedOperation.name", handler).watch(
            "ownedOperation.isAbstract", handler
        ).watch("ownedOperation.visibility", handler).watch(
            "ownedOperation.returnResult.lowerValue", handler
        ).watch(
            "ownedOperation.returnResult.upperValue", handler
        ).watch(
            "ownedOperation.returnResult.typeValue", handler
        ).watch(
            "ownedOperation.formalParameter.lowerValue", handler
        ).watch(
            "ownedOperation.formalParameter.upperValue", handler
        ).watch(
            "ownedOperation.formalParameter.typeValue", handler
        ).watch(
            "ownedOperation.formalParameter.defaultValue", handler
        ).subscribe_all()

        builder.connect_signals(
            {
                "show-operations-changed": (self._on_show_operations_change,),
                "operations-name-edited": (on_text_cell_edited, self.model, 0),
                "operations-abstract-edited": (on_bool_cell_edited, self.model, 1),
                "operations-static-edited": (on_bool_cell_edited, self.model, 2),
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
                "operations-keypress": (on_keypress_event,),
            }
        )

        return builder.get_object("operations-editor")

    @transactional
    def _on_show_operations_change(self, button, gparam):
        self.item.show_operations = button.get_active()
        self.item.request_update()


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 20

    DEPENDENCY_TYPES = (
        (gettext("Dependency"), UML.Dependency),
        (gettext("Usage"), UML.Usage),
        (gettext("Realization"), UML.Realization),
        (gettext("Implementation"), UML.Implementation),
    )

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = self.item.watcher()
        self.builder = new_builder("dependency-editor")

    def construct(self):
        dependency_combo = self.builder.get_object("dependency-combo")
        model = ComboModel(self.DEPENDENCY_TYPES)
        dependency_combo.set_model(model)

        automatic = self.builder.get_object("automatic")
        automatic.set_active(self.item.auto_dependency)

        self.update()

        self.watcher.watch("subject", self._on_subject_change).subscribe_all()

        self.builder.connect_signals(
            {
                "dependency-type-changed": (self._on_dependency_type_change,),
                "automatic-changed": (self._on_auto_dependency_change,),
                "dependency-type-destroy": (self.watcher.unsubscribe_all,),
            }
        )

        return self.builder.get_object("dependency-editor")

    def _on_subject_change(self, event):
        self.update()

    def update(self):
        """
        Update dependency type combo box.

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
            UML.model.swap_element(subject, cls)
            self.item.request_update()

    @transactional
    def _on_auto_dependency_change(self, switch, gparam):
        self.item.auto_dependency = switch.get_active()
        self.update()


def _dummy_handler(*args):
    pass


@PropertyPages.register(AssociationItem)
class AssociationPropertyPage(PropertyPageBase):
    """
    """

    NAVIGABILITY = (None, False, True)
    AGGREGATION = ("none", "shared", "composite")

    order = 20

    def __init__(self, item):
        self.item = item
        self.subject = item.subject
        self.watcher = item.subject and self.subject.watcher()
        self.semaphore = 0

    def construct_end(self, builder, end_name, end):
        subject = end.subject
        title = builder.get_object(f"{end_name}-title")
        title.set_text(f"{end_name.title()} (: {subject.type.name})")

        self.update_end_name(builder, end_name, subject)

        navigation = builder.get_object(f"{end_name}-navigation")
        navigation.set_active(self.NAVIGABILITY.index(subject.navigability))

        aggregation = builder.get_object(f"{end_name}-aggregation")
        aggregation.set_active(self.AGGREGATION.index(subject.aggregation))

        stereotypes = UML.model.get_stereotypes(subject)
        if stereotypes:
            stereotype_list = builder.get_object(f"{end_name}-stereotype-list")
            model, toggle_handler, set_value_handler = stereotype_model(subject)
            stereotype_list.set_model(model)
            return {
                f"{end_name}-toggle-stereotype": toggle_handler,
                f"{end_name}-set-slot-value": set_value_handler,
            }
        else:
            stereotype_frame = builder.get_object(f"{end_name}-stereotype-frame")
            stereotype_frame.destroy()
            return {
                f"{end_name}-toggle-stereotype": (_dummy_handler,),
                f"{end_name}-set-slot-value": (_dummy_handler,),
            }

    def update_end_name(self, builder, end_name, subject):
        name = builder.get_object(f"{end_name}-name")
        new_name = (
            UML.format(subject, visibility=True, is_derived=True, multiplicity=True,)
            or ""
        )
        if not (name.is_focus() or self.semaphore):
            self.semaphore += 1
            name.set_text(new_name)
            self.semaphore -= 1
        return name

    def construct(self):
        if not self.subject:
            return None

        builder = new_builder("association-editor")

        head = self.item.head_end
        tail = self.item.tail_end

        show_direction = builder.get_object("show-direction")
        show_direction.set_active(self.item.show_direction)

        head_signal_handlers = self.construct_end(builder, "head", head)
        tail_signal_handlers = self.construct_end(builder, "tail", tail)

        def handler(event):
            end_name = "head" if event.element is head.subject else "tail"
            self.update_end_name(builder, end_name, event.element)

        # Watch on association end:
        self.watcher.watch("memberEnd[Property].name", handler).watch(
            "memberEnd[Property].aggregation", handler
        ).watch("memberEnd[Property].visibility", handler).watch(
            "memberEnd[Property].lowerValue", handler
        ).watch(
            "memberEnd[Property].upperValue", handler
        ).subscribe_all()

        builder.connect_signals(
            {
                "show-direction-changed": (self._on_show_direction_change,),
                "invert-direction-changed": (self._on_invert_direction_change,),
                "head-name-changed": (self._on_end_name_change, head),
                "head-navigation-changed": (self._on_end_navigability_change, head),
                "head-aggregation-changed": (self._on_end_aggregation_change, head),
                "tail-name-changed": (self._on_end_name_change, tail),
                "tail-navigation-changed": (self._on_end_navigability_change, tail),
                "tail-aggregation-changed": (self._on_end_aggregation_change, tail),
                "association-editor-destroy": (self.watcher.unsubscribe_all,),
                **head_signal_handlers,
                **tail_signal_handlers,
            }
        )

        return builder.get_object("association-editor")

    @transactional
    def _on_show_direction_change(self, button, gparam):
        self.item.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.item.invert_direction()

    @transactional
    def _on_end_name_change(self, entry, end):
        if not self.semaphore:
            self.semaphore += 1
            UML.parse(end.subject, entry.get_text())
            self.semaphore -= 1

    @transactional
    def _on_end_navigability_change(self, combo, end):
        UML.model.set_navigability(
            end.subject.association, end.subject, self.NAVIGABILITY[combo.get_active()]
        )

    @transactional
    def _on_end_aggregation_change(self, combo, end):
        end.subject.aggregation = self.AGGREGATION[combo.get_active()]
