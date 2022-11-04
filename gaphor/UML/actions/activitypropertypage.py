from gaphor.diagram.hoversupport import widget_add_hover_support
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    on_text_cell_edited,
)
from gaphor.lazygi import Gtk
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.classes.classespropertypages import on_keypress_event

new_builder = new_resource_builder("gaphor.UML.actions")


@PropertyPages.register(ActivityItem)
class ActivityItemPage(PropertyPageBase):

    order = 40

    def __init__(self, item: ActivityItem):
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        from gaphor.UML.actions.gtkmodels import ActivityParameters

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
