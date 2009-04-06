"""
The file service is responsible for loading and saving the user data.
"""

from zope import interface
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, toggle_action, build_action_group
from gaphor.ui.toplevelwindow import ToplevelWindow
from gaphor.ui.propertyeditor import PropertyEditor


class InfoWindow(ToplevelWindow):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    properties = inject('properties')

    title = _("Info")
    size = (300, 300)
    menu_xml = """
      <ui>
        <toolbar action="mainwindow-toolbar">
          <placeholder name="right">
            <separator expand="true" />
            <toolitem action="Info:open" position="bot" />
          </placeholder>
        </toolbar>
      </ui>
    """

    def __init__(self):
        self.action_group = build_action_group(self)
        self.window = None

    def init(self, app):
        self._app = app

    def shutdown(self):
        pass

        
    @toggle_action(name='Info:open', stock_id='gtk-info')
    def info(self, active):
        if active:
            if not self.window:
                self.construct()
                self.window.set_keep_above(True)
                self.window.connect('delete-event', self.close)
                self.window.connect('delete-event', self.window.hide_on_delete)
            else:
               self.window.show_all()
        else:
            self.window.hide()

    def ui_component(self):
       self.property_editor = PropertyEditor()
       pe_notebook = self.property_editor.construct()
       pe_notebook.set_size_request(-1, 50)

       pe_notebook.show()
       return pe_notebook


    def close(self, widget=None, event=None):
        self.action_group.get_action('Info:open').set_active(False)

# vim:sw=4:et:ai
