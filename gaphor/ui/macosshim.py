from gi.repository import GLib, Gtk


def init_macos_shortcuts():
    """Add <Cmd>-<..> shortcuts for macOS."""

    def new_shortcut_with_args(shortcut, signal, *args):
        shortcut = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
            action=Gtk.SignalAction.new(signal),
        )
        if args:
            shortcut.set_arguments(GLib.Variant.new_tuple(*args))
        return shortcut

    def add_move_binding(widget_class, shortcut, step, count):
        widget_class.add_shortcut(
            new_shortcut_with_args(
                shortcut,
                "move-cursor",
                GLib.Variant.new_int32(step),
                GLib.Variant.new_int32(count),
                GLib.Variant.new_boolean(False),
            )
        )

        widget_class.add_shortcut(
            new_shortcut_with_args(
                "|".join(f"<Shift>{s}" for s in shortcut.split("|")),
                "move-cursor",
                GLib.Variant.new_int32(step),
                GLib.Variant.new_int32(count),
                GLib.Variant.new_boolean(True),
            )
        )

    for widget_class in (Gtk.Text, Gtk.TextView):
        for shortcut, signal in (
            ("<Meta>x", "cut-clipboard"),
            ("<Meta>c", "copy-clipboard"),
            ("<Meta>v", "paste-clipboard"),
        ):
            widget_class.add_shortcut(new_shortcut_with_args(shortcut, signal))

        for shortcut, action in (
            ("<Meta>z", "text.undo"),
            ("<Meta><Shift>z", "text.redo"),
        ):
            widget_class.add_shortcut(
                Gtk.Shortcut.new(
                    trigger=Gtk.ShortcutTrigger.parse_string(shortcut),
                    action=Gtk.NamedAction.new(action),
                )
            )

        for shortcut, step, count in (
            ("<Meta>Up|<Meta>KP_Up", Gtk.MovementStep.BUFFER_ENDS, -1),
            ("<Meta>Down|<Meta>KP_Down", Gtk.MovementStep.BUFFER_ENDS, 1),
            ("<Meta>Left|<Meta>KP_Left", Gtk.MovementStep.DISPLAY_LINE_ENDS, -1),
            ("<Meta>Right|<Meta>KP_Right", Gtk.MovementStep.DISPLAY_LINE_ENDS, 1),
            ("<Alt>Left|<Alt>KP_Left", Gtk.MovementStep.WORDS, -1),
            ("<Alt>Right|<Alt>KP_Right", Gtk.MovementStep.WORDS, 1),
        ):
            add_move_binding(widget_class, shortcut, step, count)

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

    # Gtk.TextView

    Gtk.TextView.add_shortcut(
        new_shortcut_with_args("<Meta>a", "select-all", GLib.Variant.new_boolean(True))
    )
    Gtk.TextView.add_shortcut(
        new_shortcut_with_args(
            "<Meta><Shift>a", "select-all", GLib.Variant.new_boolean(False)
        )
    )


def init_macos_settings():
    """Tweak settings, so Gaphor on macOS looks alike Linux.

    Adwaita styling only requires a close button.
    """
    Gtk.Settings.get_default().set_property("gtk-decoration-layout", ":close")
