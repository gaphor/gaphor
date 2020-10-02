# coding=utf-8
"""This module has a generic FileDialog class that is used to open or save
files."""

from typing import Sequence

from gi.repository import Gtk

from gaphor.i18n import gettext


class FileDialog:
    """This is a file dialog that is used to open or save a file."""

    def __init__(
        self,
        title,
        filename=None,
        action="open",
        parent=None,
        multiple=False,
        filters=[],
    ):
        """Initialize the file dialog.

        The title parameter is the title displayed in the dialog.  The
        filename parameter will set the current file name in the dialog.
        The action is either open or save and changes the buttons
        displayed.  If the parent window parameter is supplied, the file
        dialog is set to be transient for that window.  The multiple
        parameter should be set to true if multiple files can be opened
        at once. This means that a list of filenames instead of a single
        filename string will be returned by the selection property.
        """

        self.multiple = multiple

        if action == "open":
            action = Gtk.FileChooserAction.OPEN
        else:
            action = Gtk.FileChooserAction.SAVE

        self.dialog = Gtk.FileChooserNative(title=title, action=action)

        if parent:
            self.dialog.set_transient_for(parent)

        if filename:
            self.dialog.set_current_name(filename)

    @property
    def selection(self):
        """Return the selected file or files from the dialog.

        This is used by the selection property.
        """

        response = self.dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            if self.multiple:
                selection = self.dialog.get_filenames()
            else:
                selection = self.dialog.get_filename()
        else:
            selection = ""

        return selection

    def destroy(self):
        """Destroy the GTK dialog."""

        self.dialog.destroy()


def new_filter(name, pattern, mime_type=None):
    f = Gtk.FileFilter.new()
    f.set_name(name)
    f.add_pattern(pattern)
    if mime_type:
        f.add_mime_type(mime_type)
    return f


def _file_dialog_with_filters(title, parent, action, filename, filters):
    dialog = Gtk.FileChooserNative.new(title, parent, action, None, None)

    if parent:
        dialog.set_transient_for(parent)

    if filename:
        dialog.set_current_name(filename)

    for name, pattern, mime_type in filters:
        dialog.add_filter(new_filter(name, pattern, mime_type))
    dialog.add_filter(new_filter(gettext("All Files"), "*"))
    return dialog


def open_file_dialog(title, parent=None, filename=None, filters=[]) -> Sequence[str]:
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.OPEN, filename, filters
    )
    dialog.set_select_multiple(True)

    response = dialog.run()

    return dialog.get_filenames() if response == Gtk.ResponseType.ACCEPT else []  # type: ignore[no-any-return]


def save_file_dialog(title, parent=None, filename=None, filters=[], extension=None):
    dialog = _file_dialog_with_filters(
        title, parent, Gtk.FileChooserAction.OPEN, filename, filters
    )

    response = dialog.run()

    return dialog.get_filenames() if response == Gtk.ResponseType.ACCEPT else []  # type: ignore[no-any-return]


if __name__ == "__main__":
    import sys

    action = sys.argv[1]

    files = open_file_dialog(
        f"dialog test (action={action})",
        filters=[("All Gaphor Models", "*.gaphor", "application/x-gaphor")],
    )

    print(f"Selected file: {files}")
