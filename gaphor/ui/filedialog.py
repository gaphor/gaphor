# coding=utf-8
"""This module has a generic file dialog functions that are used to open or
save files."""

import pathlib
from typing import Optional, Sequence

from gi.repository import Gtk

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


def open_file_dialog(title, parent=None, dirname=None, filters=[]) -> Sequence[str]:
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.OPEN, filters
    )
    dialog.set_select_multiple(True)
    if dirname:
        dialog.set_current_folder(dirname)

    response = dialog.run()
    dialog.destroy()

    return dialog.get_filenames() if response == Gtk.ResponseType.ACCEPT else []  # type: ignore[no-any-return]


def save_file_dialog(
    title, parent=None, filename=None, extension=None, filters=[]
) -> Optional[str]:
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
