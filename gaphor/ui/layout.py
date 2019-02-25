# -*- coding: utf-8 -*-

# Copyright © 2010 etkdocking Contributors
#
# This file is part of etkdocking.
#
# etkdocking is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# etkdocking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with etkdocking. If not, see <http://www.gnu.org/licenses/>.


from simplegeneric import generic
from xml.etree.ElementTree import fromstring

from gi.repository import Gtk

from gaphor.core import _


widget_factory = {}


def deserialize(layout, container, layoutstr, itemfactory):
    """
    Return a new layout with it's attached frames. Frames that should be floating
    already have their Gtk.Window attached (check frame.get_parent()). Transient settings
    and such should be done by the invoking application.
    """

    def counter():
        i = 0
        while True:
            yield i
            i += 1

    def _des(element, index, parent_widget=None):
        if element.tag == "component":
            name = element.attrib["name"]
            widget = itemfactory(name)
            widget.set_name(name)
            add(widget, index, parent_widget)
        else:
            factory = widget_factory[element.tag]
            widget = factory(parent=parent_widget, index=index, **element.attrib)
            assert widget, "No widget (%s)" % widget
            if len(element):
                list(map(_des, element, counter(), [widget] * len(element)))
        return widget

    tree = fromstring(layoutstr)
    list(map(layout.append, list(map(_des, tree, counter(), [container] * len(tree)))))

    # return layout


def add(widget, index, parent_widget):
    if isinstance(parent_widget, Gtk.Paned):
        if index == 0:
            parent_widget.pack1(child=widget, resize=False, shrink=False)
        elif index == 1:
            parent_widget.pack2(child=widget, resize=True, shrink=False)
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
