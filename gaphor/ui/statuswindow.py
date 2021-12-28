"""Defines a status window class for displaying the progress of a queue."""

from queue import Empty

from gi.repository import Gdk, GLib, Gtk, Pango


class StatusWindow:
    """Create a borderless window on the parent, usually the main window, with
    a label and a progress bar.

    The progress bar is updated as the queue is updated.
    """

    def __init__(self, title, message, parent=None, queue=None, display=True):
        """Create the status window.

        The title parameter is the title of the window.  The message
        parameter is a string displayed near the progress bar to
        indicate what is happening.  The parent parameter is the parent
        window to display the window in.  The queue parameter is a queue
        that is used to update the progress bar.  The display parameter
        will display the window if true.  This is the default.
        """

        self.title = title
        self.message = message
        self.parent = parent
        self.queue = queue
        self.window: Gtk.Window = None

        if display:
            self.display()

    def init_window(self):
        """Create the window GUI component.

        This will set the window and progress bar attributes so they can
        be referenced later.
        """

        frame = Gtk.Frame.new(None)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, spacing=12)
        label = Gtk.Label.new(self.message)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_size_request(400, -1)

        if Gtk.get_major_version() == 3:
            self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
            self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
            self.window.set_keep_above(True)
            self.window.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
            self.window.add(frame)
            frame.add(vbox)
            vbox.pack_start(label, True, True, 0)
            vbox.pack_start(self.progress_bar, expand=False, fill=False, padding=0)
        else:
            self.window = Gtk.Window.new()
            self.window.set_child(frame)
            frame.set_child(vbox)
            vbox.append(label)
            vbox.append(self.progress_bar)

        self.window.set_title(self.title)
        self.window.get_style_context().add_class("status-window")
        if self.parent:
            self.window.set_transient_for(self.parent)
        self.window.set_modal(True)
        self.window.set_resizable(False)
        self.window.set_decorated(False)

    def display(self):
        """Display the status window.

        If a queue has been supplied to the StatusWindow instance, a new
        gobject idle handle is created.  Once the window is destroyed,
        this handler is removed.
        """
        if not self.window:
            self.init_window()

        assert self.window

        if Gtk.get_major_version() == 3:
            self.window.show_all()
        else:
            self.window.show()

        if self.queue:
            self.idle_id = GLib.idle_add(
                progress_idle_handler,
                self.progress_bar,
                self.queue,
                priority=GLib.PRIORITY_DEFAULT_IDLE,
            )
            self.window.connect("destroy", remove_idle_handler, self.idle_id)

    def destroy(self):
        """Destroy the status window.

        This will also remove the gobject handler.
        """
        if self.window:
            self.window.destroy()
            self.window = None


def progress_idle_handler(progress_bar, queue):
    """This is a gobject idle handler that updates the supplied progress bar.

    The percentage is retrieved from the queue until it is empty.  The
    progress bar is then updated with the current percentage.
    """

    percentage = 0
    try:
        percentage = queue.get(block=False)
    except Empty:
        pass
    if percentage:
        progress_bar.set_fraction(min(percentage, 100.0) / 100.0)
    return True


def remove_idle_handler(window, idle_id):
    """This removes the supplied gobject idle id.

    This handle is required by StatusWindow when it is destroyed.
    """

    GLib.source_remove(idle_id)
