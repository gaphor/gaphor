from gi.repository import GLib, Gdk, GObject, Gtk, Pango

_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <requires lib="gtk" version="4.0"/>
  <template class="TextField" parent="GtkStack">
    <child>
      <object class="GtkStackPage">
        <property name="name">default</property>
        <property name="child">
          <object class="GtkLabel">
            <property name="xalign">0</property>
            <property name="hexpand">yes</property>
            <binding name="attributes">
              <lookup name="attributes">TextField</lookup>
            </binding>
            <binding name="label">
              <lookup name="readonly-text">TextField</lookup>
            </binding>
          </object>
        </property>
      </object>
    </child>
    <child>
      <object class="GtkStackPage">
        <property name="name">editing</property>
        <property name="child">
          <object class="GtkText" id="_text">
            <property name="propagate-text-width">yes</property>
            <property name="buffer">
              <object class="GtkEntryBuffer">
                <binding name="text">
                  <lookup name="editable-text">TextField</lookup>
                </binding>
              </object>
            </property>
          </object>
        </property>
      </object>
    </child>
  </template>
</interface>
"""


@Gtk.Template(string=_XML)
class TextField(Gtk.Stack):
    """A text input field for use in ``ListView``s.

    The Text Field contains two layers of text. One for displaying
    (a `Gtk.Label`), and one for editing (`Gtk.Text`).
    This allows us to easily define a separate text for editing.
    For example: a class attribute is represented as `+ attr: int = 0`,
    but if we edit it, we should only be able to edit it's name (`attr`).
    """

    __gtype_name__ = "TextField"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _text_field_edit_controls(self)
        self.connect("notify::readonly-text", print)

    readonly_text = GObject.Property(type=str, default="")
    editable_text = GObject.Property(type=str, default="")
    attributes = GObject.Property(type=Pango.AttrList)
    """Pango style attributes for the readonly text."""

    can_edit = GObject.Property(type=bool, default=True)

    @GObject.Property(type=bool, default=False)
    def editing(self):
        return self.get_visible_child_name() == "editing"

    @editing.setter  # type: ignore[no-redef]
    def editing(self, value):
        if value:
            GLib.timeout_add(
                START_EDIT_DELAY, lambda: self.set_visible_child_name("editing")
            )
        else:
            self.set_visible_child_name("default")

    _text = Gtk.Template.Child()

    def start_editing(self):
        self.editing = True  # type: ignore[method-assign]

    def done_editing(self, should_commit):
        if self.editing:
            self.emit("done-editing", should_commit)

    @GObject.Signal(name="done-editing", arg_types=(bool,))
    def _done_editing(self, should_commit: bool) -> None:
        self.editing = False  # type: ignore[method-assign]
        if parent := self.get_parent():
            parent.grab_focus()
        if should_commit:
            self.editable_text = self._text.get_buffer().get_text()
        else:
            self._text.get_buffer().set_text(self.editable_text, -1)


TextField.set_css_name("textfield")


def _text_field_edit_controls(text_field: TextField):
    def text_focus_out(_ctrl):
        if text_field.editing:
            text_field.done_editing(True)

    def text_key_pressed(_ctrl, keyval, _keycode, _state):
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            text_field.done_editing(True)
            return True
        elif keyval == Gdk.KEY_Escape:
            text_field.done_editing(False)
            return True
        return False

    focus_ctrl = Gtk.EventControllerFocus.new()
    focus_ctrl.connect("leave", text_focus_out)
    text_field._text.add_controller(focus_ctrl)

    key_ctrl = Gtk.EventControllerKey.new()
    key_ctrl.connect("key-pressed", text_key_pressed)
    text_field._text.add_controller(key_ctrl)

    def start_editing(text_field, _pspec):
        if text_field.get_visible_child_name() == "editing":
            text_field._text.grab_focus()

    text_field.connect("notify::visible-child-name", start_editing)
