import logging
from gi.repository import Gtk

from gaphas.decorators import AsyncIO
from gaphor import UML
from gaphor.core import _, transactional
from gaphor.services.elementdispatcher import EventWatcher
from gaphor.diagram.propertypages import PropertyPages, PropertyPageBase
from gaphor.diagram.propertypages import (
    NamedElementPropertyPage,
    NamedItemPropertyPage,
    EditableTreeModel,
    create_tree_view,
    create_hbox_label,
    create_uml_combo,
)
from gaphor.diagram.classes import (
    ClassItem,
    InterfaceItem,
    AssociationItem,
    DependencyItem,
    ImplementationItem,
)


log = logging.getLogger(__name__)


class ClassAttributes(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def _get_rows(self):
        for attr in self._item.subject.ownedAttribute:
            if not attr.association:
                yield [UML.format(attr), attr.isStatic, attr]

    def _create_object(self):
        attr = self.element_factory.create(UML.Property)
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
        operation = self.element_factory.create(UML.Operation)
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


@PropertyPages.register(UML.Class)
class ClassPropertyPage(NamedElementPropertyPage):
    """Adapter which shows a property page for a class view."""

    def __init__(self, subject):
        super().__init__(subject)

    def construct(self):
        page = super().construct()

        if not self.subject:
            return page

        # Abstract toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)
        button = Gtk.CheckButton(label=_("Abstract"))
        button.set_active(self.subject.isAbstract)

        button.connect("toggled", self._on_abstract_change)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        return page

    @transactional
    def _on_abstract_change(self, button):
        self.subject.isAbstract = button.get_active()


@PropertyPages.register(InterfaceItem)
class InterfacePropertyPage(NamedItemPropertyPage):
    """Adapter which shows a property page for an interface view."""

    def construct(self):
        page = super().construct()
        item = self.item

        # Fold toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(_("Folded"))
        button.set_active(item.folded)
        button.connect("toggled", self._on_fold_change)

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        allowed = (DependencyItem, ImplementationItem)
        can_fold = (
            len(connected_items) == 0
            or len(connected_items) == 1
            and isinstance(connected_items[0], allowed)
        )

        button.set_sensitive(can_fold)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        return page

    @transactional
    def _on_fold_change(self, button):
        item = self.item

        connected_items = [c.item for c in item.canvas.get_connections(connected=item)]
        assert len(connected_items) <= 1

        line = None
        if len(connected_items) == 1:
            line = connected_items[0]

        fold = button.get_active()

        if fold:
            item.folded = item.FOLDED_PROVIDED
        else:
            item.folded = item.FOLDED_NONE

        if line:
            if fold and isinstance(line, DependencyItem):
                item.folded = item.FOLDED_REQUIRED

            line._solid = fold
            constraint = line.canvas.get_connection(line.head).constraint
            constraint.ratio_x = 0.5
            constraint.ratio_y = 0.5
            line.request_update()


@PropertyPages.register(ClassItem)
class AttributesPage(PropertyPageBase):
    """An editor for attributes associated with classes and interfaces."""

    order = 20
    name = "Attributes"

    def __init__(self, item):
        super(AttributesPage, self).__init__()
        self.item = item
        self.watcher = EventWatcher(item.subject)

    def construct(self):
        page = Gtk.VBox()

        if not self.item.subject:
            return page

        # Show attributes toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        hbox.pack_start(label, False, True, 0)
        button = Gtk.CheckButton(label=_("Show attributes"))
        button.set_active(self.item.show_attributes)
        button.connect("toggled", self._on_show_attributes_change)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        def create_model():
            return ClassAttributes(self.item, (str, bool, object))

        self.model = create_model()

        tip = """\
Add and edit class attributes according to UML syntax. Attribute syntax examples
- attr
- + attr: int
- # /attr: int
"""
        tree_view = create_tree_view(self.model, (_("Attributes"), _("S")), tip)
        page.pack_start(tree_view, True, True, 0)

        @AsyncIO(single=True)
        def handler(event):
            # Single it's asynchronous, make sure all properties are still there
            if not tree_view.props.has_focus and self.item and self.item.subject:
                self.model = create_model()
                tree_view.set_model(self.model)

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
        ).register_handlers()
        tree_view.connect("destroy", self.watcher.unregister_handlers)
        return page

    @transactional
    def _on_show_attributes_change(self, button):
        self.item.show_attributes = button.get_active()
        self.item.request_update()


@PropertyPages.register(ClassItem)
class OperationsPage(PropertyPageBase):
    """An editor for operations associated with classes and interfaces."""

    order = 30
    name = "Operations"

    def __init__(self, item):
        super(OperationsPage, self).__init__()
        self.item = item
        self.watcher = EventWatcher(item.subject)

    def construct(self):
        page = Gtk.VBox()

        if not self.item.subject:
            return page

        # Show operations toggle
        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        hbox.pack_start(label, False, True, 0)
        button = Gtk.CheckButton(label=_("Show operations"))
        button.set_active(self.item.show_operations)
        button.connect("toggled", self._on_show_operations_change)
        hbox.pack_start(button, True, True, 0)
        page.pack_start(hbox, False, True, 0)

        def create_model():
            return ClassOperations(self.item, (str, bool, bool, object))

        self.model = create_model()
        tip = """\
Add and edit class operations according to UML syntax. Operation syntax examples
- call()
- + call(a: int, b: str)
- # call(a: int: b: str): bool
"""
        tree_view = create_tree_view(self.model, (_("Operation"), _("A"), _("S")), tip)
        page.pack_start(tree_view, True, True, 0)

        @AsyncIO(single=True)
        def handler(event):
            if not tree_view.props.has_focus and self.item and self.item.subject:
                self.model = create_model()
                tree_view.set_model(self.model)

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
        ).register_handlers()
        tree_view.connect("destroy", self.watcher.unregister_handlers)

        return page

    @transactional
    def _on_show_operations_change(self, button):
        self.item.show_operations = button.get_active()
        self.item.request_update()


@PropertyPages.register(DependencyItem)
class DependencyPropertyPage(PropertyPageBase):
    """Dependency item editor."""

    order = 0

    DEPENDENCY_TYPES = (
        (_("Dependency"), UML.Dependency),
        (_("Usage"), UML.Usage),
        (_("Realization"), UML.Realization),
        (_("Implementation"), UML.Implementation),
    )

    def __init__(self, item):
        super(DependencyPropertyPage, self).__init__()
        self.item = item
        self.size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.watcher = EventWatcher(self.item)

    def construct(self):
        page = Gtk.VBox()

        hbox = create_hbox_label(self, page, _("Dependency type"))

        self.combo = create_uml_combo(
            self.DEPENDENCY_TYPES, self._on_dependency_type_change
        )
        hbox.pack_start(self.combo, False, True, 0)

        hbox = create_hbox_label(self, page, "")

        button = Gtk.CheckButton(_("Automatic"))
        button.set_active(self.item.auto_dependency)
        button.connect("toggled", self._on_auto_dependency_change)
        hbox.pack_start(button, True, True, 0)

        self.watcher.watch("subject", self._on_subject_change).register_handlers()
        button.connect("destroy", self.watcher.unregister_handlers)

        self.update()

        return page

    def _on_subject_change(self, event):
        self.update()

    def update(self):
        """
        Update dependency type combo box.

        Disallow dependency type when dependency is established.
        """
        combo = self.combo
        item = self.item
        index = combo.get_model().get_index(item.dependency_type)
        combo.props.sensitive = not item.auto_dependency
        combo.set_active(index)

    @transactional
    def _on_dependency_type_change(self, combo):
        combo = self.combo
        cls = combo.get_model().get_value(combo.get_active())
        self.item.dependency_type = cls
        subject = self.item.subject
        if subject:
            UML.model.swap_element(subject, cls)
            self.item.request_update()

    @transactional
    def _on_auto_dependency_change(self, button):
        self.item.auto_dependency = button.get_active()
        self.update()


@PropertyPages.register(AssociationItem)
class AssociationPropertyPage(NamedItemPropertyPage):
    """
    """

    def construct_end(self, title, end):

        if not end.subject:
            return None

        # TODO: use Gtk.Frame here
        frame = Gtk.Frame.new("%s (: %s)" % (title, end.subject.type.name))
        vbox = Gtk.VBox()
        vbox.set_border_width(6)
        vbox.set_spacing(6)
        frame.add(vbox)

        self.create_pages(end, vbox)

        return frame

    def construct(self):
        page = super(AssociationPropertyPage, self).construct()

        if not self.subject:
            return page

        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(label=_("Show direction"))
        button.set_active(self.item.show_direction)
        button.connect("toggled", self._on_show_direction_change)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button(label=_("Invert Direction"))
        button.connect("clicked", self._on_invert_direction_change)
        hbox.pack_start(button, True, True, 0)

        page.pack_start(hbox, False, True, 0)

        box = self.construct_end(_("Head"), self.item.head_end)
        if box:
            page.pack_start(box, False, True, 0)

        box = self.construct_end(_("Tail"), self.item.tail_end)
        if box:
            page.pack_start(box, False, True, 0)

        self.update()

        return page

    def update(self):
        pass

    @transactional
    def _on_show_direction_change(self, button):
        self.item.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.item.invert_direction()

    def get_adapters(self, item):
        """
        Return an ordered list of (order, name, adapter).
        """
        adaptermap = {}
        try:
            if item.subject:
                for adapter in PropertyPages(item.subject):
                    adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)
        except AttributeError:
            pass
        for adapter in PropertyPages(item):
            adaptermap[adapter.name] = (adapter.order, adapter.name, adapter)

        adapters = sorted(adaptermap.values())
        return adapters

    def create_pages(self, item, vbox):
        """
        Load all tabs that can operate on the given item.

        The first item will not contain a title.
        """
        adapters = self.get_adapters(item)

        first = True
        for _, name, adapter in adapters:
            try:
                page = adapter.construct()
                if page is None:
                    continue
                if first:
                    vbox.pack_start(page, False, True, 0)
                    first = False
                else:
                    expander = Gtk.Expander()
                    expander.set_use_markup(True)
                    expander.set_label("<b>%s</b>" % name)
                    expander.add(page)
                    expander.show_all()
                    vbox.pack_start(expander, False, True, 0)
            except Exception as e:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )


@PropertyPages.register(UML.Property)
class AssociationEndPropertyPage(PropertyPageBase):
    """Property page for association end properties."""

    order = 0

    NAVIGABILITY = [None, False, True]

    def __init__(self, subject):
        self.subject = subject
        self.watcher = EventWatcher(subject)

    def construct(self):
        vbox = Gtk.VBox()

        entry = Gtk.Entry()
        # entry.set_text(UML.format(self.subject, visibility=True, is_derived=Truemultiplicity=True) or '')

        # monitor subject attribute (all, cause it contains many children)
        changed_id = entry.connect("changed", self._on_end_name_change)

        def handler(event):
            if not entry.props.has_focus:
                entry.handler_block(changed_id)
                entry.set_text(
                    UML.format(
                        self.subject,
                        visibility=True,
                        is_derived=True,
                        multiplicity=True,
                    )
                    or ""
                )
                # entry.set_text(UML.format(self.subject, multiplicity=True) or '')
                entry.handler_unblock(changed_id)

        handler(None)

        self.watcher.watch("name", handler).watch("aggregation", handler).watch(
            "visibility", handler
        ).watch("lowerValue", handler).watch("upperValue", handler).register_handlers()
        entry.connect("destroy", self.watcher.unregister_handlers)

        vbox.pack_start(entry, True, True, 0)

        entry.set_tooltip_text(
            """\
Enter attribute name and multiplicity, for example
- name
+ name [1]
- name [1..2]
~ 1..2
- [1..2]\
"""
        )

        combo = Gtk.ComboBoxText()
        for t in ("Unknown navigation", "Not navigable", "Navigable"):
            combo.append_text(t)

        nav = self.subject.navigability
        combo.set_active(self.NAVIGABILITY.index(nav))

        combo.connect("changed", self._on_navigability_change)
        vbox.pack_start(combo, False, True, 0)

        combo = Gtk.ComboBoxText()
        for t in ("No aggregation", "Shared", "Composite"):
            combo.append_text(t)

        combo.set_active(
            ["none", "shared", "composite"].index(self.subject.aggregation)
        )

        combo.connect("changed", self._on_aggregation_change)
        vbox.pack_start(combo, False, True, 0)

        return vbox

    @transactional
    def _on_end_name_change(self, entry):
        UML.parse(self.subject, entry.get_text())

    @transactional
    def _on_navigability_change(self, combo):
        nav = self.NAVIGABILITY[combo.get_active()]
        UML.model.set_navigability(self.subject.association, self.subject, nav)

    @transactional
    def _on_aggregation_change(self, combo):
        self.subject.aggregation = ("none", "shared", "composite")[combo.get_active()]
