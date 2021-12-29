from gi.repository import Gdk, Gtk

if Gtk.get_major_version() == 3:

    def widget_add_hover_support(widget):
        widget.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        def hover(widget, event):
            widget.set_state_flags(Gtk.StateFlags.PRELIGHT, False)

        def unhover(widget, event):
            widget.unset_state_flags(Gtk.StateFlags.PRELIGHT)

        widget.connect("motion-notify-event", hover)
        widget.connect("leave-notify-event", unhover)

    def flowbox_add_hover_support(flowbox):
        flowbox.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        hover_child: Gtk.Widget = None

        def hover(widget, event):
            nonlocal hover_child
            child = widget.get_child_at_pos(event.x, event.y)
            if hover_child and child is not hover_child:
                hover_child.unset_state_flags(Gtk.StateFlags.PRELIGHT)
            if child:
                child.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
            hover_child = child

        def unhover(widget, event):
            if hover_child:
                hover_child.unset_state_flags(Gtk.StateFlags.PRELIGHT)

        flowbox.connect("motion-notify-event", hover)
        flowbox.connect("leave-notify-event", unhover)

else:

    def widget_add_hover_support(widget):
        pass

    def flowbox_add_hover_support(flowbox):
        pass
