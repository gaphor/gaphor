"""The element editor is a utility window used for editing elements."""

import gtk
from zope import interface
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, toggle_action, build_action_group
from gaphor.ui.toplevelwindow import UtilityWindow
from gaphor.ui.propertyeditor import PropertyEditor

class ElementEditor(UtilityWindow):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    interface.implements(IActionProvider)

    element_factory = inject('element_factory')
    properties = inject('properties')

    title = _("Element Editor")
    size = (275, -1)
    resizable = True
    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="edit">
            <menuitem action="ElementEditor:open" />
            <separator />
          </menu>
        </menubar>
        <toolbar action="mainwindow-toolbar">
          <placeholder name="right">
            <toolitem action="ElementEditor:open" position="bot" />
          </placeholder>
        </toolbar>
      </ui>
    """

    def __init__(self):
        """Constructor.  Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        
        self.action_group = build_action_group(self)
        self.window = None
        self.property_editor = PropertyEditor()
        self.widget = self.property_editor.construct()

    @toggle_action(name='ElementEditor:open', label=_('Editor'), stock_id='gtk-edit', accel='<Control>e')
    def elementeditor(self, active):
        """Display the element editor when the toolbar button is toggled.  If
        active, the element editor is displayed.  Otherwise, it is hidden."""
        
        if active:
            if not self.window:
                self.construct()
                self.window.connect('delete-event', self.close)
                self.window.connect('key-press-event', self.on_key_press_event)
            else:
                self.window.show_all()
        else:
            self.window.hide()

    def ui_component(self):
        """Display and return the PropertyEditor widget."""
        
        self.widget.show()
        return self.widget

    def close(self, widget=None, event=None):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""
        
        self.action_group.get_action('ElementEditor:open').set_active(False)
        self.window.hide()
        return True

    def on_key_press_event(self, widget, event):
        """Close the element editor window if the escape key was pressed."""
        
        if event.keyval == gtk.keysyms.Escape:
            self.close()

# vim:sw=4:et:ai
