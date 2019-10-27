"""
Layout code from a simple XML description.
"""

from typing import Dict, Callable
from xml.etree.ElementTree import fromstring

from gi.repository import Gtk


widget_factory: Dict[str, Callable] = {}


def deserialize(layout, container, layoutstr, itemfactory):
    """
    Return a new layout with it's attached frames. Frames that should be floating
    already have their Gtk.Window attached (check frame.get_parent()). Transient settings
    and such should be done by the invoking application.
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
            widget = factory(parent=parent_widget, index=index, **element.attrib)
            assert widget, f"No widget ({widget})"
            for i, e in enumerate(element):
                _des(e, i, widget)
        return widget

    tree = fromstring(layoutstr)
    for index, element in enumerate(tree):
        layout.append(_des(element, index, container))


def add(widget, index, parent_widget, resize=False, shrink=False):
    if isinstance(parent_widget, Gtk.Paned):
        if index == 0:
            parent_widget.pack1(child=widget, resize=resize, shrink=shrink)
        elif index == 1:
            parent_widget.pack2(child=widget, resize=resize, shrink=shrink)
    elif isinstance(parent_widget, Gtk.Box):
        parent_widget.pack_start(widget, resize, resize, 2)
    else:
        parent_widget.add(widget)


def factory(typename):
    """
    Simple decorator for populating the widget_factory dictionary.
    """

    def _factory(func):
        widget_factory[typename] = func
        return func

    return _factory


@factory("paned")
def paned(parent, index, orientation, position=None):
    paned = Gtk.Paned.new(
        Gtk.Orientation.HORIZONTAL
        if orientation == "horizontal"
        else Gtk.Orientation.VERTICAL
    )
    add(paned, index, parent)
    if position:
        paned.set_position(int(position))
    paned.show()
    return paned


@factory("box")
def box(parent, index, orientation):
    box = Gtk.Box.new(
        Gtk.Orientation.HORIZONTAL
        if orientation == "horizontal"
        else Gtk.Orientation.VERTICAL,
        0,
    )
    add(box, index, parent)
    box.show()
    return box
