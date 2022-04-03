import logging
from typing import Optional

from gaphas.tool.rubberband import RubberbandState
from gi.repository import Gtk, Pango

from gaphor.core import gettext

log = logging.getLogger(__name__)


example_hazardous_events = [
    (
        "Highway Driving Straight at Speed",
        "E4",
        "Everyday exposure to city, roads, highways, freeways",
        "Driving at Speed",
        "Traffic Free Flow",
        "Highway",
        "Any Road Condition",
        "Any Environmental Condition",
    ),
    (
        "Highway While Turning",
        "E3",
        "Turning on Highway is < 10% of average operating time",
        "Driving at Speed\n Turning",
        "Traffic Free Flow",
        "Highway",
        "Any Road Condition",
        "Any Environmental Condition",
    ),
]


class TablePage:

    if Gtk.get_major_version() == 3:
        VIEW_TARGET_STRING = 0
        VIEW_TARGET_ELEMENT_ID = 1
        VIEW_TARGET_TOOLBOX_ACTION = 2
        VIEW_DND_TARGETS = [
            Gtk.TargetEntry.new("gaphor/element-id", 0, VIEW_TARGET_ELEMENT_ID),
            Gtk.TargetEntry.new("gaphor/toolbox-action", 0, VIEW_TARGET_TOOLBOX_ACTION),
        ]

    def __init__(
        self, diagram, event_manager, element_factory, properties, modeling_language
    ):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.properties = properties
        self.diagram = diagram
        self.modeling_language = modeling_language

        self.view = None
        self.grid: Optional[Gtk.Grid] = None
        self.widget: Optional[Gtk.Widget] = None
        self.diagram_css: Optional[Gtk.CssProvider] = None

        self.rubberband_state = RubberbandState()

    title = property(lambda s: s.diagram and s.diagram.name or gettext("<None>"))

    def get_diagram(self):
        return self.diagram

    def get_view(self):
        return self.view

    def construct(self):
        """Create the widget.

        Returns: the newly created widget.
        """
        assert self.diagram

        # Creating the ListStore model
        self.hara_liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
        for hazardous_event in example_hazardous_events:
            self.hara_liststore.append(list(hazardous_event))
        self.current_filter_language = None

        self.treeview = Gtk.TreeView(model=self.hara_liststore)

        for i, column_title in enumerate(
            [
                "Name",
                "Exposure",
                "Justification of Exposure",
                "Vehicle Usage",
                "Traffic And People",
                "Location",
                "Road Condition",
                "Environmental Condition",
            ]
        ):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", True)
            renderer.set_property("wrap-mode", Pango.WrapMode.WORD)
            renderer.set_property("wrap-width", 100)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_min_width(50)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_resizable(True)
            column.set_reorderable(True)
            self.treeview.append_column(column)
            self.treeview.columns_autosize()

        self.diagram_css = Gtk.CssProvider.new()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        if Gtk.get_major_version() == 3:
            scrolled_window.add(self.treeview)
            scrolled_window.show_all()
        else:
            scrolled_window.set_child(self.treeview)

        self.widget = scrolled_window
        return self.widget

    def close(self):
        """Tab is destroyed.

        Do the same thing that would be done if Close was pressed.
        """
        assert self.widget
        if Gtk.get_major_version() == 3:
            self.widget.destroy()
        elif parent := self.widget.get_parent():
            parent.remove(self.widget)
