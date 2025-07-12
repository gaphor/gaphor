"""Defines a status window class for displaying the progress of a queue."""

from __future__ import annotations

from gi.repository import Adw, GLib, Gtk, Pango

from gaphor.asyncio import sleep


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
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        label = Gtk.Label.new(message)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        vbox.append(label)

        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_size_request(400, -1)
        vbox.append(self.progress_bar)

        self.window = Adw.Dialog.new()
        self.window.set_child(vbox)
        self.window.set_title(title)
        self.window.add_css_class("status-window")
        self.window.present(parent)

    async def progress(self, percentage: float):
        """Update progress percentage (0..100)."""
        if self.progress_bar:
            self.progress_bar.set_fraction(min(percentage, 100.0) / 100.0)
        await sleep(0)

    def done(self):
        """Close the status window."""
        if self.window:
            if GLib.main_depth() > 0:
                # If we close the status window to quick it will stay around
                # See https://gitlab.gnome.org/GNOME/libadwaita/-/issues/970
                window = self.window
                GLib.idle_add(window.close, priority=GLib.PRIORITY_LOW)
            else:
                self.window.close()
            self.window = None
