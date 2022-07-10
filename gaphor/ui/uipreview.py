"""Show GTK 4 UI Components.

Usage:
  python -m  gaphor.ui.uipreview <ui file>
"""
import os
import sys
import xml.etree.ElementTree as etree

from gi.repository import Adw, Gio, GLib, Gtk

from gaphor.ui.styling import Styling


def load_components(ui_filename):
    with open(ui_filename) as ui_file:
        ui_xml = load_ui_file(ui_file)

    builder = Gtk.Builder.new_from_string(ui_xml, -1)
    components = [
        o
        for o in builder.get_objects()
        if isinstance(o, Gtk.Widget) and not o.get_parent()
    ]

    for component in components:
        print("show component", component.get_buildable_id())
        yield component.get_buildable_id(), component


def load_ui_file(ui_file) -> str:
    ui_xml = etree.parse(ui_file)
    for node in ui_xml.findall(".//*[signal]"):
        for signal in node.findall("signal"):
            node.remove(signal)
    return etree.tostring(ui_xml.getroot(), encoding="unicode", method="xml")


def in_window(app, name, component):
    window = Gtk.Window.new()
    window.set_child(component)
    window.set_title(name)
    window.set_default_size(226, -1)
    window.show()
    app.add_window(window)
    return window


def app_open(app, files, n_files, hint):
    Styling()
    file = files[0].get_path()
    last_modified = 0.0
    components: dict[str, Gtk.Window] = {}

    def monitor_file(_=None):
        nonlocal last_modified
        try:
            new_mtime = os.stat(file).st_mtime
            if new_mtime > last_modified:
                last_modified = new_mtime
                for name, comp in load_components(file):
                    if name in components:
                        components[name].set_child(comp)
                    else:
                        components[name] = in_window(app, name, comp)
        except Exception as e:
            print(e)
        return True

    s = GLib.Timeout(1000)
    s.set_callback(monitor_file)
    s.attach()
    monitor_file()


if __name__ == "__main__":
    if Gtk.get_major_version() != 4:
        print("UI Preview works with GTK 4 only.")
        sys.exit(1)

    app = Adw.Application(
        application_id="org.gaphor.UIPreview", flags=Gio.ApplicationFlags.HANDLES_OPEN
    )
    app.connect("open", app_open)
    app.run(sys.argv)
