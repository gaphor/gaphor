from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.format import format, parse
from gaphor.diagram.hoversupport import widget_add_hover_support
from gaphor.diagram.propertypages import (
    EditableTreeModel,
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    on_text_cell_edited,
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
                "tree-view-destroy": (self.watcher.unsubscribe_all,),
            },
        )

        self.info = builder.get_object("parameters-info")
        if Gtk.get_major_version() == 3:
            widget_add_hover_support(builder.get_object("parameters-info-icon"))
        else:
            help_link(builder, "parameters-info-icon", "parameters-info")

        tree_view: Gtk.TreeView = builder.get_object("parameter-list")
        tree_view.set_model(self.model)
        if Gtk.get_major_version() == 3:
            controller = self.key_controller = Gtk.EventControllerKey.new(tree_view)
        else:
            controller = Gtk.EventControllerKey.new()
            tree_view.add_controller(controller)
        controller.connect("key-pressed", on_keypress_event, tree_view)

        return builder.get_object("activity-editor")

    def on_parameters_info_clicked(self, image, event):
        self.info.show()
