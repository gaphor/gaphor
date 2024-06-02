from gi.repository import Gdk, GLib, GObject, Gtk, Pango

START_EDIT_DELAY = 100  # ms

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
            <property name="ellipsize">end</property>
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
            <child>
              <object class="GtkEventControllerFocus">
                <signal name="leave" handler="on_text_focus_out" />
              </object>
            </child>
            <child>
              <object class="GtkEventControllerKey">
                <signal name="key-pressed" handler="on_text_key_pressed" />
              </object>
            </child>
          </object>
        </property>
      </object>
    </child>
    <child>
      <object class="GtkStackPage">
        <property name="name">placeholder</property>
        <property name="child">
          <object class="GtkLabel">
            <property name="xalign">0</property>
            <property name="hexpand">yes</property>
            <binding name="label">
              <lookup name="placeholder-text">TextField</lookup>
            </binding>
            <style>
              <class name="dim-label" />
            </style>
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
        self._readonly_text = ""

    editable_text = GObject.Property(type=str, default="")
    placeholder_text = GObject.Property(type=str, default="")
    attributes = GObject.Property(type=Pango.AttrList)
    """Pango style attributes for the readonly text."""

    can_edit = GObject.Property(type=bool, default=True)

    @GObject.Property(type=str, default="")
    def readonly_text(self):
        return self._readonly_text

    @readonly_text.setter  # type: ignore[no-redef]
    def readonly_text(self, value):
        self._readonly_text = value or ""
        self.set_visible_child_name("default" if value else "placeholder")

    @GObject.Property(type=bool, default=False)
    def editing(self):
        return self.get_visible_child_name() == "editing"

    @editing.setter  # type: ignore[no-redef]
    def editing(self, value):
        if not self.can_edit:
            return

        if value:

            def _start_editing():
                self.set_visible_child_name("editing")
                self._text.grab_focus()

            GLib.timeout_add(START_EDIT_DELAY, _start_editing)
        else:
            self.set_visible_child_name(
                "default" if self.readonly_text else "placeholder"
            )

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

    @Gtk.Template.Callback()
    def on_text_focus_out(self, _ctrl):
        if self.editing:
            self.done_editing(True)

    @Gtk.Template.Callback()
    def on_text_key_pressed(self, _ctrl, keyval, _keycode, _state):
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.done_editing(True)
            return True
        elif keyval == Gdk.KEY_Escape:
            self.done_editing(False)
            return True
        return False


TextField.set_css_name("textfield")
