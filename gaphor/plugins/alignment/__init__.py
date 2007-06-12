"""
This plugin extends Gaphor with XMI alignment actions.
"""

__version__ = "0.1"
__author__ = "Jeroen Vloothuis"

from zope import interface, component
from gaphor.core import inject, transactional, action, build_action_group
from gaphor.interfaces import IService, IActionProvider
from gaphor.ui.interfaces import IDiagramSelectionChange


class Alignment(object):

    interface.implements(IService, IActionProvider)

    gui_manager = inject('gui_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="diagram">
            <placeholder name="ternary">
              <separator />
              <menuitem action="align-horizontal" />
              <menuitem action="align-vertical" />
            </placeholder>
          </menu>
        </menubar>
      </ui>"""

    def __init__(self):
        self.action_group = build_action_group(self)
        self._last_update = None

    def init(self, app):
	self._app = app
        app.registerHandler(self.update)
    
    def shutdown(self):
        self._app.unregisterHandler(self.update)

    @component.adapter(IDiagramSelectionChange)
    def update(self, event=None):
        self._last_update = event
        sensitive = event and len(event.selected_items) > 1
        self.action_group.get_action('align-horizontal').set_sensitive(sensitive)
        self.action_group.get_action('align-vertical').set_sensitive(sensitive)

    def get_items(self):
        return (self._last_update and self._last_update.selected_items) or []
        
    def moveItemsToTarget(self, items, target_x, target_y):
        for item in items:
            if target_x is not None:
                x = target_x - item.matrix[4]
            else:
                x = 0
            if target_y is not None:
                y = target_y - item.matrix[5]
            else:
                y = 0
            item.matrix.translate(x,y)
            item.request_update()
            
    def getXCoords(self, items):
        return [item.matrix[4] for item in items]

    @action(name='align-vertical', label='Align vertical',
            tooltip="Align diagram elements vertically")
    @transactional
    def align_vertical(self):
        items = self.get_items()
        target_x=min(self.getXCoords(items))
        target_y=None
        self.moveItemsToTarget(items, target_x, target_y)

    def getYCoords(self, items):
        return [item.matrix[5] for item in items]

    @action(name='align-horizontal', label='Align horizontal',
            tooltip="Align diagram elements horizontally")
    @transactional
    def align_horizontal(self):
        items = self.get_items()
        target_y = min(self.getYCoords(items))
        target_x = None
        self.moveItemsToTarget(items, target_x, target_y)


# vim:sw=4:et:ai
