# coding=utf-8
"""This module has a generic file dialog functions that are used to open or
save files."""

from __future__ import annotations

import pathlib

from gi.repository import Gio, Gtk

from gaphor.i18n import gettext

GAPHOR_FILTER = [(gettext("All Gaphor Models"), "*.gaphor", "application/x-gaphor")]


def new_filter(name, pattern, mime_type=None):
    f = Gtk.FileFilter.new()
    f.set_name(name)
    f.add_pattern(pattern)
    if mime_type:
        f.add_mime_type(mime_type)
    return f


def _file_dialog_with_filters(title, parent, action, filters):
    dialog = Gtk.FileChooserNative.new(title, parent, action, None, None)

    if parent:
        dialog.set_transient_for(parent)

    for name, pattern, mime_type in filters:
        dialog.add_filter(new_filter(name, pattern, mime_type))
    dialog.add_filter(new_filter(gettext("All Files"), "*"))
    return dialog


def open_file_dialog(title, handler, parent=None, dirname=None, filters=None) -> None:
    if filters is None:
        filters = []
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.OPEN, filters
    )
    dialog.set_select_multiple(True)

    def response(_dialog, answer):
        if Gtk.get_major_version() == 3:
            filenames = (
                dialog.get_filenames() if answer == Gtk.ResponseType.ACCEPT else []
            )
        else:
            filenames = (
                [f.get_path() for f in dialog.get_files()]
                if answer == Gtk.ResponseType.ACCEPT
                else []
            )
            dialog.destroy()
        handler(filenames)

    dialog.connect("response", response)
    if Gtk.get_major_version() == 3:
        if dirname:
            dialog.set_current_folder(dirname)
        dialog.run()
        dialog.destroy()
    else:
        if dirname:
            dialog.set_current_folder(Gio.File.new_for_path(dirname))
        dialog.show()


def save_file_dialog(
    title, parent=None, filename=None, extension=None, filters=None
) -> str | None:
    if filters is None:
        filters = []
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.SAVE, filters
    )
    dialog.set_do_overwrite_confirmation(True)
    if filename:
        dialog.set_filename(filename)

    try:
        while dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()

            if extension and not filename.endswith(extension):
                filename += extension
                if pathlib.Path(filename).exists():
                    dialog.set_filename(filename)
                    continue
            return filename  # type: ignore[no-any-return]
    finally:
        dialog.destroy()
    return None


if __name__ == "__main__":
    import sys

    action = sys.argv[1]

    files = save_file_dialog(
        f"dialog test (action={action})",
        extension=".gaphor",
        filters=GAPHOR_FILTER,
    )

    print(f"Selected file: {files}")
