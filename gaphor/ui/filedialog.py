"""This module has a generic FileDialog class that is used to open
or save files."""

from builtins import object
from gi.repository import Gtk


class FileDialog(object):
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
        """Initialize the file dialog.  The title parameter is the title
        displayed in the dialog.  The filename parameter will set the current
        file name in the dialog.  The action is either open or save and changes
        the buttons displayed.  If the parent window parameter is supplied,
        the file dialog is set to be transient for that window.  The multiple
        parameter should be set to true if multiple files can be opened at once.
        This means that a list of filenames instead of a single filename string
        will be returned by the selection property.  The filters is a list
        of dictionaries that have a name and pattern key.  This restricts what
        is visible in the dialog."""

        self.multiple = multiple

        if action == "open":
            action = Gtk.FileChooserAction.OPEN
            response_button = Gtk.STOCK_OPEN
        else:
            action = Gtk.FileChooserAction.SAVE
            response_button = Gtk.STOCK_SAVE

        buttons = (
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            response_button,
            Gtk.ResponseType.OK,
        )

        self.dialog = Gtk.FileChooserDialog(title=title, action=action, buttons=buttons)

        if parent:
            self.dialog.set_transient_for(parent)

        if filename:
            self.dialog.set_current_name(filename)

        for filter in filters:
            _filter = Gtk.FileFilter()
            _filter.set_name(filter["name"])
            _filter.add_pattern(filter["pattern"])
            self.dialog.add_filter(_filter)

    def get_selection(self):
        """Return the selected file or files from the dialog.  This is used
        by the selection property."""

        response = self.dialog.run()

        if response == Gtk.ResponseType.OK:
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

    selection = property(get_selection)
