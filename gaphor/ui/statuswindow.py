"""Defines a status window class for displaying the progress of a queue."""
from __future__ import annotations


from gaphas.decorators import g_async
from gi.repository import Adw, Gtk, Pango


class StatusWindow:
    """Create a borderless window on the parent, usually the main window, with
    a label and a progress bar.

    The progress bar is updated as the queue is updated.
    """

    def __init__(self, title: str, message: str, parent: Gtk.Widget | None = None):
        """Create the status window.

        The title parameter is the title of the window.  The message
        parameter is a string displayed near the progress bar to
        indicate what is happening.  The parent parameter is the parent
        window to display the window in.
        """

        self.title = title
        self.message = message
        self.parent = parent
        self.window: Gtk.Widget = None

        self.display()

    def init_window(self):
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        label = Gtk.Label.new(self.message)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        vbox.append(label)

        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_size_request(400, -1)
        vbox.append(self.progress_bar)

        self.window = Adw.Dialog.new()
        self.window.set_child(vbox)
        self.window.set_title(self.title)

        self.window.add_css_class("status-window")

    @g_async()
    def display(self):
        if not self.window:
            self.init_window()

        assert self.window

        self.window.present(self.parent)

    def progress(self, percentage: int):
        """Update progress percentage (0..100)."""
        if self.progress_bar:
            self.progress_bar.set_fraction(min(percentage, 100.0) / 100.0)

    def destroy(self):
        """Destroy the status window.

        This will also remove the gobject handler.
        """
        if self.window:
            self.window.close()
            self.window = None
