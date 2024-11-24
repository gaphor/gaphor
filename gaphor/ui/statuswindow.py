"""Defines a status window class for displaying the progress of a queue."""

from gi.repository import GLib, Gtk, Pango


class StatusWindow:
    """Create a borderless window on the parent, usually the main window, with
    a label and a progress bar.

    The progress bar is updated as the queue is updated.
    """

    def __init__(self, title, message, parent=None):
        """Create the status window.

        The title parameter is the title of the window.  The message
        parameter is a string displayed near the progress bar to
        indicate what is happening.  The parent parameter is the parent
        window to display the window in.
        """
        frame = Gtk.Frame.new(None)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        label = Gtk.Label.new(message)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_size_request(400, -1)

        self.window = Gtk.Window.new()
        self.window.set_child(frame)
        frame.set_child(vbox)
        vbox.append(label)
        vbox.append(self.progress_bar)

        self.window.set_title(title)
        self.window.add_css_class("status-window")
        if parent:
            self.window.set_transient_for(parent)
        self.window.set_modal(True)
        self.window.set_resizable(False)
        self.window.set_decorated(False)

    def progress(self, percentage: int):
        """Update progress percentage (0..100)."""
        if self.progress_bar:
            self.progress_bar.set_fraction(min(percentage, 100.0) / 100.0)

    def done(self):
        """Close the status window."""
        if self.window:
            # Allow the GUI to do some upates before we actually close the dialog
            GLib.idle_add(self.window.close, priority=GLib.PRIORITY_LOW)
            self.window = None
