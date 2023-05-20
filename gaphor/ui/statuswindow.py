"""Defines a status window class for displaying the progress of a queue."""


from gaphas.decorators import g_async
from gi.repository import Gtk, Pango


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

        self.title = title
        self.message = message
        self.parent = parent
        self.window: Gtk.Window = None

        self.display()

    def init_window(self):
        frame = Gtk.Frame.new(None)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        label = Gtk.Label.new(self.message)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_size_request(400, -1)

        self.window = Gtk.Window.new()
        self.window.set_child(frame)
        frame.set_child(vbox)
        vbox.append(label)
        vbox.append(self.progress_bar)

        self.window.set_title(self.title)
        self.window.add_css_class("status-window")
        if self.parent:
            self.window.set_transient_for(self.parent)
        self.window.set_modal(True)
        self.window.set_resizable(False)
        self.window.set_decorated(False)

    @g_async()
    def display(self):
        if not self.window:
            self.init_window()

        assert self.window

        self.window.set_visible(True)

    def progress(self, percentage: int):
        """Update progress percentage (0..100)."""
        if self.progress_bar:
            self.progress_bar.set_fraction(min(percentage, 100.0) / 100.0)

    def destroy(self):
        """Destroy the status window.

        This will also remove the gobject handler.
        """
        if self.window:
            self.window.destroy()
            self.window = None
