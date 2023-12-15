from gi.repository import Gdk, GObject, Gtk, Pango


class TextFieldModel(GObject.Object):
    __gtype_name__ = "TextFieldModel"

    readonly_text = GObject.Property(type=str, default="")
    editable_text = GObject.Property(type=str, default="")
    attributes = GObject.Property(type=Pango.AttrList)
    """Pango style attributes for the readonly text."""

    allow_editing = GObject.Property(type=bool, default=True)

    mode = GObject.Property(type=str, default="default")
    """(Internal) View state, either "default" or "editing" mode.
    """

    def start_editing(self):
        """Editing mode can be initialized from the model.

        In a ``Gtk.ListView`` we do not have direct access to the
        widgets, so we need an indirect way to initialize edit mode.
        """
        if self.allow_editing:
            self.mode = "editing"


_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <requires lib="gtk" version="4.0"/>
  <template class="TextField" parent="GtkStack">
    <binding name="visible-child-name">
      <lookup name="mode" type="TextFieldModel">
        <lookup name="model">TextField</lookup>
      </lookup>
    </binding>
    <child>
      <object class="GtkStackPage">
        <property name="name">default</property>
        <property name="child">
          <object class="GtkLabel">
            <property name="xalign">0</property>
            <property name="hexpand">yes</property>
            <binding name="attributes">
              <lookup name="attributes" type="TextFieldModel">
                <lookup name="model">TextField</lookup>
              </lookup>
            </binding>
            <binding name="label">
              <lookup name="readonly_text" type="TextFieldModel">
                <lookup name="model">TextField</lookup>
              </lookup>
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
                  <lookup name="editable_text" type="TextFieldModel">
                    <lookup name="model">TextField</lookup>
                  </lookup>
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

    def __init__(self, model: TextFieldModel | None = None):
        super().__init__(model=model)
        _text_field_edit_controls(self)

    model = GObject.Property(type=TextFieldModel)
    _text = Gtk.Template.Child()

    @property
    def is_editing(self) -> bool:
        return bool(self.get_visible_child_name() == "editing")

    def done_editing(self, should_commit):
        if self.is_editing:
            self.emit("done-editing", should_commit)

    @GObject.Signal(name="done-editing", arg_types=(bool,))
    def _done_editing(self, should_commit: bool) -> None:
        self.model.mode = "default"
        if parent := self.get_parent():
            parent.grab_focus()
        if should_commit:
            self.model.editable_text = self._text.get_buffer().get_text()
        else:
            self._text.get_buffer().set_text(self.model.editable_text, -1)


TextField.set_css_name("textfield")


def _text_field_edit_controls(text_field: TextField):
    def text_focus_out(_ctrl):
        if text_field.is_editing:
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
