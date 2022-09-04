# coding=utf-8
"""This module has a generic file dialog functions that are used to open or
save files."""

from __future__ import annotations

from pathlib import Path

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
    dialog.set_modal(True)
    if Gtk.get_major_version() == 3:
        if dirname:
            dialog.set_current_folder(dirname)
    else:
        if dirname:
            dialog.set_current_folder(Gio.File.parse_name(dirname))
    dialog.show()


def save_file_dialog(
    title,
    handler,
    parent=None,
    filename=None,
    extension=None,
    filters=None,
) -> None:
    if filters is None:
        filters = []
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.SAVE, filters
    )

    def get_filename() -> Path:
        if Gtk.get_major_version() == 3:
            return Path(dialog.get_filename())
        else:
            return Path(dialog.get_file().get_path())

    def set_filename(filename: Path):
        if Gtk.get_major_version() == 3:
            dialog.set_filename(str(filename.name))
        else:
            dialog.set_current_name(str(filename.name))

    def overwrite_check() -> Path | None:
        filename = get_filename()
        if extension and filename.suffix != extension:
            filename = filename.with_suffix(extension)
            set_filename(filename)
            return None if filename.exists() else filename
        return filename

    def response(_dialog, answer):
        if answer == Gtk.ResponseType.ACCEPT:
            if filename := overwrite_check():
                dialog.destroy()
                handler(filename)
            else:
                dialog.show()
        else:
            dialog.destroy()

    dialog.connect("response", response)
    if filename:
        set_filename(filename)
    if Gtk.get_major_version() == 3:
        dialog.set_do_overwrite_confirmation(True)
        if filename:
            dialog.set_current_folder(str(filename.parent))
    else:
        if filename:
            dialog.set_current_folder(Gio.File.parse_name(str(filename.parent)))
    dialog.set_modal(True)
    dialog.show()
