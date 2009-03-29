"""
The file service is responsible for loading and saving the user data.
"""

from zope import interface
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, build_action_group
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

        
    @action(name='Info:open', stock_id='gtk-info')
    def info(self):
        if not self.window:
            self.construct()
            self.window.set_keep_above(True)
            self.window.connect('destroy', self.close)
        else:
           self.window.show_all()


    def ui_component(self):
       self.property_editor = PropertyEditor()
       pe_notebook = self.property_editor.construct()
       pe_notebook.set_size_request(-1, 50)

       pe_notebook.show()
       return pe_notebook


    def close(self, window=None):
        self.window.destroy()
        self.window = None

# vim:sw=4:et:ai
