try:
    import gi
    from gi.repository import GLib, Gtk

    if Gtk.get_major_version() == 3:
        gi.require_version("GtkosxApplication", "1.0")
    else:
        raise ValueError()
except ValueError:

    def macos_init(application):
        pass

else:
    from gi.repository import GtkosxApplication

    macos_app = GtkosxApplication.Application.get()

    def open_file(macos_app, path, application):
        if path == __file__:
            return False

        application.new_session(filename=path)

        return True

    def block_termination(macos_app, application):
        quit = application.quit()
        return not quit

    def macos_init(application):
        macos_app.connect("NSApplicationOpenFile", open_file, application)
        macos_app.connect(
            "NSApplicationBlockTermination", block_termination, application
        )


if Gtk.get_major_version == 4:

    def new_shortcut_with_args(shortcut, name, *args):
        shortcut = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
            action=Gtk.SignalAction.new(name),
        )
        if args:
            shortcut.set_arguments(GLib.Variant.new_tuple(*args))
        return shortcut

    # MacOS specific key bindings:
    # Command–a: Select all.
    # Command–Shift-a: Unselect all.
    # Command–Up Arrow: Move the insertion point to the beginning of the document.
    # Command–Down Arrow: Move the insertion point to the end of the document.
    # Command–Left Arrow: Move the insertion point to the beginning of the current line.
    # Command–Right Arrow: Move the insertion point to the end of the current line.
    # Option–Left Arrow: Move the insertion point to the beginning of the previous word.
    # Option–Right Arrow: Move the insertion point to the end of the next word.

    # Control-H: Delete the character to the left of the insertion point. Or use Delete.
    # Control-D: Delete the character to the right of the insertion point. Or use Fn-Delete.

    # Gtk.Text

    Gtk.Text.add_shortcut(
        Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("<Meta>a"),
            action=Gtk.CallbackAction.new(lambda self, data: self.select_region(0, -1)),
        )
    )
    Gtk.Text.add_shortcut(
        new_shortcut_with_args(
            "<Meta><Shift>a",
            "move-cursor",
            GLib.Variant.new_int32(Gtk.MovementStep.VISUAL_POSITIONS),
            GLib.Variant.new_int32(0),
            GLib.Variant.new_boolean(False),
        )
    )

    Gtk.Text.add_shortcut(
        new_shortcut_with_args(
            "<Meta>Up",
            "move-cursor",
            GLib.Variant.new_int32(Gtk.MovementStep.VISUAL_POSITIONS),
            GLib.Variant.new_int32(0),
            GLib.Variant.new_boolean(False),
        )
    )
    Gtk.Text.add_shortcut(
        new_shortcut_with_args(
            "<Meta>Down",
            "move-cursor",
            GLib.Variant.new_int32(Gtk.MovementStep.VISUAL_POSITIONS),
            GLib.Variant.new_int32(-1),
            GLib.Variant.new_boolean(False),
        )
    )

    # Gtk.TextView

    Gtk.TextView.add_shortcut(
        new_shortcut_with_args("<Meta>a", "select-all", GLib.Variant.new_boolean(True))
    )
    Gtk.TextView.add_shortcut(
        new_shortcut_with_args(
            "<Meta><Shift>a", "select-all", GLib.Variant.new_boolean(False)
        )
    )

    for cls in (Gtk.Text, Gtk.TextView):
        for shortcut, signal in [
            ("<Meta>x", "cut-clipboard"),
            ("<Meta>c", "copy-clipboard"),
            ("<Meta>v", "paste-clipboard"),
        ]:
            cls.add_shortcut(
                Gtk.Shortcut.new(
                    trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
                    action=Gtk.SignalAction.new(signal),
                )
            )

        for shortcut, action in [
            ("<Meta>z", "text.undo"),
            ("<Meta><Shift>z", "text.redo"),
        ]:
            cls.add_shortcut(
                Gtk.Shortcut.new(
                    trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
                    action=Gtk.NamedAction.new(action),
                )
            )
