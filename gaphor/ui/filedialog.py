"""This module has a generic file dialog functions that are used to open or
save files."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

from gi.repository import Gio, Gtk

from gaphor.i18n import gettext

GAPHOR_FILTER = [(gettext("Gaphor Models"), "*.gaphor", "application/x-gaphor")]


def new_filter(name: str, pattern: str, mime_type: str | None = None) -> Gtk.FileFilter:
    f = Gtk.FileFilter.new()
    f.set_name(name)
    f.add_pattern(pattern)
    if mime_type and sys.platform != "win32":
        f.add_mime_type(mime_type)
    return f


def new_image_filter() -> Gtk.FileFilter:
    f = Gtk.FileFilter.new()
    f.set_name(gettext("Images"))
    f.add_pixbuf_formats()
    return f


def new_filters(filters, images=False):
    store = Gio.ListStore.new(Gtk.FileFilter)
    if images:
        store.append(new_image_filter())
    if filters:
        for name, pattern, mime_type in filters:
            store.append(new_filter(name, pattern, mime_type))
    store.append(new_filter(gettext("All Files"), "*"))
    return store


def open_file_dialog(
    title,
    handler,
    parent=None,
    dirname=None,
    filters=None,
    image_filter=False,
) -> None:
    dialog = Gtk.FileDialog.new()
    dialog.set_title(title)

    if dirname:
        dialog.set_initial_folder(Gio.File.parse_name(dirname))

    dialog.set_filters(new_filters(filters, image_filter))

    def response(dialog, result):
        if result.had_error():
            # File dialog was cancelled
            return

        files = dialog.open_multiple_finish(result)
        handler([Path(f.get_path()) for f in files])

    dialog.open_multiple(parent=parent, cancellable=None, callback=response)


def save_file_dialog(
    title: str,
    filename: Path,
    handler: Callable[[Path], None],
    parent=None,
    filters=None,
) -> Gtk.FileChooser:
    dialog = Gtk.FileDialog.new()
    dialog.set_title(title)
    dialog.set_initial_file(Gio.File.parse_name(str(filename.absolute())))

    dialog.set_filters(new_filters(filters))

    def response(dialog, result):
        if result.had_error():
            # File dialog was cancelled
            return

        filename = Path(dialog.save_finish(result).get_path())
        handler(filename)

    dialog.save(parent=parent, cancellable=None, callback=response)
    return dialog


def pretty_path(path: Path) -> str:
    if path.is_relative_to(Path.home()):
        return str(path).replace(str(Path.home()), "~", 1)
    elif hasattr(os, "getuid"):
        document_portal_dir = f"/run/user/{os.getuid()}/doc"
        if path.is_relative_to(document_portal_dir):
            return f"{path.name} ({gettext('Flatpak Document Portal')})"
    return str(path)
