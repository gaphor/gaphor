#!/usr/bin/env python
# vim:sw=4:et:
"""
Title: Live Object Browser
Submitter: Simon Burton (other recipes)
Last Updated: 2004/08/18
Version no: 1.0
Category: Debugging

Description:

Given an object, this tool throws up a gtk tree widget that maps all the references found. It dynamically builds the tree, which means it can handle large amounts of data and circular references.
"""

from gi.repository import Gtk


class Browser:
    def make_row(self, piter, name, value):
        info = repr(value)
        if not hasattr(value, "__dict__"):
            if len(info) > 80:
                # it's a big list, or dict etc.
                info = info[:80] + "..."
        _piter = self.treestore.append(piter, [name, type(value).__name__, info])
        return _piter

    def make_instance(self, value, piter):
        if hasattr(value, "__dict__"):
            for _name, _value in list(value.__dict__.items()):
                _piter = self.make_row(piter, "." + _name, _value)
                _path = self.treestore.get_path(_piter)
                self.otank[_path] = (_name, _value)

    def make_mapping(self, value, piter):
        keys = []
        if hasattr(value, "keys"):
            keys = list(value.keys())
        elif hasattr(value, "__len__"):
            keys = list(range(len(value)))
        for key in keys:
            _name = "[%s]" % str(key)
            _piter = self.make_row(piter, _name, value[key])
            _path = self.treestore.get_path(_piter)
            self.otank[_path] = (_name, value[key])

    def make(self, name=None, value=None, path=None, depth=1):
        if path is None:
            # make root node
            piter = self.make_row(None, name, value)
            path = self.treestore.get_path(piter)
            self.otank[path] = (name, value)
        else:
            name, value = self.otank[path]

        piter = self.treestore.get_iter(path)
        if not self.treestore.iter_has_child(piter):
            self.make_mapping(value, piter)
            self.make_instance(value, piter)

        if depth:
            for i in range(self.treestore.iter_n_children(piter)):
                self.make(path=path + (i,), depth=depth - 1)

    def row_expanded(self, treeview, piter, path):
        self.make(path=path)

    def delete_event(self, widget, event, data=None):
        self.window.destroy()
        # Gtk.main_quit()
        return False

    def __init__(self, name, value):
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Browser")
        self.window.set_size_request(512, 320)
        self.window.connect("delete_event", self.delete_event)

        # we will store the name, the type name, and the repr
        columns = [str, str, str]
        self.treestore = Gtk.TreeStore(*columns)

        # the otank tells us what object we put at each node in the tree
        self.otank = {}  # map path -> (name,value)
        self.make(name, value)

        self.treeview = Gtk.TreeView(self.treestore)
        self.treeview.connect("row-expanded", self.row_expanded)

        self.tvcolumns = [Gtk.TreeViewColumn() for _type in columns]
        i = 0
        for tvcolumn in self.tvcolumns:
            self.treeview.append_column(tvcolumn)
            cell = Gtk.CellRendererText()
            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, "text", i)
            i = i + 1

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolled_window.add(self.treeview)

        self.window.add(scrolled_window)
        self.window.show_all()


def dump(name, value):
    browser = Browser(name, value)
    Gtk.main()


def test():
    class Nil:
        pass

    a = Nil()
    b = Nil()
    c = Nil()
    d = Nil()
    a.b = b
    b.c = c
    c.d = d
    d.a = a  # circular chain
    dump("a", a)


if __name__ == "__main__":
    test()
