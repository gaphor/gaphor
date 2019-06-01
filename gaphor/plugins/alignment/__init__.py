"""
This plugin extends Gaphor with XMI alignment actions.
"""

from gaphor.core import inject, event_handler, transactional, action, build_action_group
from gaphor.abc import Service, ActionProvider
from gaphor.ui.event import DiagramSelectionChange


class Alignment(Service, ActionProvider):

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="diagram">
            <placeholder name="ternary">
              <separator />
              <menuitem action="align-left" />
              <menuitem action="align-center" />
              <menuitem action="align-right" />
              <separator />
              <menuitem action="align-top" />
              <menuitem action="align-bottom" />
              <menuitem action="align-middle" />
            </placeholder>
          </menu>
        </menubar>
      </ui>"""

    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.action_group = build_action_group(self)
        self._last_update = None
        self.event_manager.subscribe(self.update)
        self.update()

    def init(self, app):
        pass

    def shutdown(self):
        self.event_manager.unsubscribe(self.update)

    @event_handler(DiagramSelectionChange)
    def update(self, event=None):
        self._last_update = event
        sensitive = event and len(event.selected_items) > 1
        if sensitive is not None:
            self.action_group.get_action("align-left").set_sensitive(sensitive)
            self.action_group.get_action("align-center").set_sensitive(sensitive)
            self.action_group.get_action("align-right").set_sensitive(sensitive)
            self.action_group.get_action("align-top").set_sensitive(sensitive)
            self.action_group.get_action("align-middle").set_sensitive(sensitive)
            self.action_group.get_action("align-bottom").set_sensitive(sensitive)

    def get_items(self):
        return (self._last_update and self._last_update.selected_items) or []

    def get_focused_item(self):
        return self._last_update.focused_item

    def getXCoordsLeft(self, items):
        return [item.matrix[4] for item in items]

    def getXCoordsRight(self, items):
        return [item.matrix[4] + item.width for item in items]

    def getYCoordsTop(self, items):
        return [item.matrix[5] for item in items]

    def getYCoordsBottom(self, items):
        return [item.matrix[5] + item.height for item in items]

    @action(
        name="align-left",
        label="Left",
        tooltip="Vertically align diagram elements on the left",
        accel="<Primary><Shift>l",
    )
    @transactional
    def align_left(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        target_x = fitem.matrix[4]
        for item in items:
            x = target_x - item.matrix[4]
            item.matrix.translate(x, 0)
            item.request_update()

    @action(
        name="align-center",
        label="Center",
        tooltip="Vertically align diagram elements on their centers",
        accel="<Primary><Shift>c",
    )
    @transactional
    def align_center(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        min_x = min(self.getXCoordsLeft(items))
        max_x = max(self.getXCoordsRight(items))
        center_x = fitem.matrix[4] + (fitem.width / 2)
        for item in items:
            x = center_x - (item.width / 2) - item.matrix[4]
            item.matrix.translate(x, 0)
            item.request_update()

    @action(
        name="align-right",
        label="Right",
        tooltip="Vertically align diagram elements on the right",
        accel="<Primary><Shift>r",
    )
    @transactional
    def align_right(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        target_x = fitem.matrix[4] + fitem.width
        for item in items:
            x = target_x - item.width - item.matrix[4]
            item.matrix.translate(x, 0)
            item.request_update()

    @action(
        name="align-top",
        label="Top",
        tooltip="Horizontally align diagram elements on their tops",
        accel="<Primary><Shift>t",
    )
    @transactional
    def align_top(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        target_y = fitem.matrix[5]
        for item in items:
            y = target_y - item.matrix[5]
            item.matrix.translate(0, y)
            item.request_update()

    @action(
        name="align-middle",
        label="Middle",
        tooltip="Horizontally align diagram elements on their middles",
        accel="<Primary><Shift>m",
    )
    @transactional
    def align_middle(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        middle_y = fitem.matrix[5] + (fitem.height / 2)
        for item in items:
            y = middle_y - (item.height / 2) - item.matrix[5]
            item.matrix.translate(0, y)
            item.request_update()

    @action(
        name="align-bottom",
        label="Bottom",
        tooltip="Horizontally align diagram elements on their bottoms",
        accel="<Primary><Shift>b",
    )
    @transactional
    def align_bottom(self):
        items = self.get_items()
        fitem = self.get_focused_item()
        target_y = fitem.matrix[5] + fitem.height
        for item in items:
            y = target_y - item.height - item.matrix[5]
            item.matrix.translate(0, y)
            item.request_update()
