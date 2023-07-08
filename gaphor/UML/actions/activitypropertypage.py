from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    EditableTreeModel,
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    new_builder as diagram_new_builder,
    handler_blocking,
    on_text_cell_edited,
    unsubscribe_all_on_destroy,
)
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.classes.classespropertypages import on_keypress_event

new_builder = new_resource_builder("gaphor.UML.actions")


class ActivityParameters(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def __init__(self, item):
        super().__init__(item, cols=(str, object))

    def get_rows(self):
        for node in self._item.subject.node:
            if isinstance(node, UML.ActivityParameterNode):
                yield [format(node.parameter), node]

    def create_object(self):
        model = self._item.model
        node = model.create(UML.ActivityParameterNode)
        node.parameter = model.create(UML.Parameter)
        self._item.subject.node = node
        return node

    @transactional
    def set_object_value(self, row, col, value):
        node = row[-1]
        if col == 0:
            parse(node.parameter, value)
            row[0] = format(node.parameter)
        elif col == 1:
            # Value in attribute object changed:
            row[0] = format(node.parameter)

    def swap_objects(self, o1, o2):
        return self._item.subject.node.swap(o1, o2)

    def sync_model(self, new_order):
        self._item.subject.node.order(
            lambda key: new_order.index(key) if key in new_order else -1
        )


@PropertyPages.register(ActivityItem)
class ActivityItemPage(PropertyPageBase):
    order = 40

    def __init__(self, item: ActivityItem):
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        subject = self.item.subject

        if not subject:
            return

        self.model = ActivityParameters(self.item)

        builder = new_builder(
            "activity-editor",
            "parameters-info",
            signals={
                "parameter-edited": (on_text_cell_edited, self.model, 0),
                "parameters-info-clicked": (self.on_parameters_info_clicked),
            },
        )

        self.info = builder.get_object("parameters-info")
        help_link(builder, "parameters-info-icon", "parameters-info")

        tree_view: Gtk.TreeView = builder.get_object("parameter-list")
        tree_view.set_model(self.model)
        controller = Gtk.EventControllerKey.new()
        tree_view.add_controller(controller)
        controller.connect("key-pressed", on_keypress_event, tree_view)

        return unsubscribe_all_on_destroy(
            builder.get_object("activity-editor"), self.watcher
        )

    def on_parameters_info_clicked(self, image, event):
        self.info.set_visible(True)


@PropertyPages.register(UML.ActivityParameterNode)
class ActivityParameterNodeNamePropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject):
        assert subject is None or hasattr(subject, "name")
        super().__init__()
        self.subject = subject
        self.watcher = subject.watcher() if subject else None

    def construct(self):
        if not self.subject:
            return

        assert self.watcher
        builder = diagram_new_builder(
            "name-editor",
        )

        subject = self.subject

        entry = builder.get_object("name-entry")
        entry.set_text(subject and subject.parameter and subject.parameter.name or "")

        @handler_blocking(entry, "changed", self._on_name_changed)
        def handler(event):
            if event.element is subject and event.new_value != entry.get_text():
                entry.set_text(event.new_value or "")

        self.watcher.watch("parameter.name", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("name-editor"), self.watcher
        )

    @transactional
    def _on_name_changed(self, entry):
        if self.subject.parameter.name != entry.get_text():
            self.subject.parameter.name = entry.get_text()
