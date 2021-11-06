"""Layout code from a simple XML description."""

from typing import Callable, Dict
from xml.etree.ElementTree import fromstring

from gi.repository import Gdk, Gtk

if Gtk.get_major_version() == 3:

    def is_maximized(window: Gtk.Window) -> bool:
        window_state = window.get_window().get_state()
        return window_state & (Gdk.WindowState.MAXIMIZED | Gdk.WindowState.FULLSCREEN)  # type: ignore[no-any-return]

else:

    def is_maximized(window: Gtk.Window) -> bool:
        return window.is_maximized()  # type: ignore[no-any-return]


widget_factory: Dict[str, Callable] = {}


def deserialize(container, layoutstr, itemfactory, properties):
    """Return a new layout with it's attached frames.

    Frames that should be floating already have their Gtk.Window
    attached (check frame.get_parent()). Transient settings and such
    should be done by the invoking application.
    """

    def _des(element, index, parent_widget=None):
        if element.tag == "component":
            name = element.attrib["name"]
            resize = element.attrib.get("resize", "false") == "true"
            widget = itemfactory(name)
            widget.set_name(name)
            add(widget, index, parent_widget, resize)
        else:
            factory = widget_factory[element.tag]
            widget = factory(
                parent=parent_widget,
                index=index,
                properties=properties,
                **element.attrib,
            )
            assert widget, f"No widget ({widget})"
            for i, e in enumerate(element):
                _des(e, i, widget)
        return widget

    layout = []
    tree = fromstring(layoutstr)
    for index, element in enumerate(tree):
        layout.append(_des(element, index, container))
    return layout


if Gtk.get_major_version() == 3:

    def add(widget, index, parent_widget, resize=False, shrink=False):
        if isinstance(parent_widget, Gtk.Paned):
            if index == 0:
                parent_widget.pack1(child=widget, resize=resize, shrink=shrink)
            elif index == 1:
                parent_widget.pack2(child=widget, resize=resize, shrink=shrink)
        elif isinstance(parent_widget, Gtk.Box):
            parent_widget.pack_start(widget, resize, resize, 0)
        else:
            parent_widget.add(widget)

else:

    def add(widget, index, parent_widget, resize=False, shrink=False):
        if isinstance(parent_widget, Gtk.Paned):
            if index == 0:
                parent_widget.set_start_child(widget)
            elif index == 1:
                parent_widget.set_end_child(widget)
        elif isinstance(parent_widget, Gtk.Box):
            parent_widget.append(widget)
        else:
            parent_widget.set_child(widget)
        widget.set_hexpand_set(True)
        widget.set_hexpand(resize)


def factory(typename):
    """Simple decorator for populating the widget_factory dictionary."""

    def _factory(func):
        widget_factory[typename] = func
        return func

    return _factory


def _position_changed(paned, _gparam, properties):
    window = paned.get_toplevel() if Gtk.get_major_version() == 3 else paned.get_root()
    if not is_maximized(window):
        properties.set(paned.get_name(), paned.props.position)


@factory("paned")
def paned(parent, index, properties, name, orientation, position=None):
    paned = Gtk.Paned.new(
        Gtk.Orientation.HORIZONTAL
        if orientation == "horizontal"
        else Gtk.Orientation.VERTICAL
    )
    paned.set_name(name)
    add(paned, index, parent)
    paned.set_position(properties.get(name, int(position)))
    paned.connect("notify::position", _position_changed, properties)
    paned.show()
    return paned


@factory("box")
def box(parent, index, properties, orientation, resize="false"):
    box = Gtk.Box.new(
        Gtk.Orientation.HORIZONTAL
        if orientation == "horizontal"
        else Gtk.Orientation.VERTICAL,
        0,
    )
    add(box, index, parent, resize == "true")
    box.show()
    return box
