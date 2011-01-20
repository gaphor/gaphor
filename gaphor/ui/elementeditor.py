"""The element editor is a utility window used for editing elements."""

import gtk
from zope import interface
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, build_action_group
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
            <separator />
            <menuitem action="ElementEditor:open" />
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        """Constructor.  Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        
        self.action_group = build_action_group(self)
        self.dock_item = None
        self.property_editor = PropertyEditor()
        self.widget = self.property_editor.construct()

    @action(name='ElementEditor:open', label=_('Editor'), stock_id='gtk-edit', accel='<Control>e')
    def elementeditor(self):
        """Display the element editor when the toolbar button is toggled.  If
        active, the element editor is displayed.  Otherwise, it is hidden."""
        
        if not self.widget.get_parent():
            self.construct()
            self.dock_item.connect('close', self.on_close)

    def ui_component(self):
        """Display and return the PropertyEditor widget."""
        
        self.widget.show()
        return self.widget

    def on_close(self, item):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""
        
        log.debug('ElementEditor.close')
        self.action_group.get_action('ElementEditor:open').set_active(False)
        self.widget.unparent()
        self.dock_item.destroy()
        return True

#    def on_key_press_event(self, widget, event):
#        """Close the element editor window if the escape key was pressed."""
#        
#        if event.keyval == gtk.keysyms.Escape:
#            self.close()

# vim:sw=4:et:ai
