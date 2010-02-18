"""
The file service is responsible for loading and saving the user data.
"""

import gtk
from zope import interface
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, toggle_action, build_action_group
from gaphor.ui.toplevelwindow import UtilityWindow
from gaphor.ui.propertyeditor import PropertyEditor


class ElementEditor(UtilityWindow):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

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
        self.action_group = build_action_group(self)
        self.window = None
        self.property_editor = PropertyEditor()
        self.widget = self.property_editor.construct()

    @toggle_action(name='ElementEditor:open', label=_('Editor'), stock_id='gtk-edit', accel='<Control>e')
    def elementeditor(self, active):
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
        self.widget.show()
        return self.widget


    def close(self, widget=None, event=None):
        self.action_group.get_action('ElementEditor:open').set_active(False)
        self.window.hide()
        return True

    def on_key_press_event(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.close()


# vim:sw=4:et:ai
