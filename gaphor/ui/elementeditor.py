"""The element editor is a utility window used for editing elements."""

import logging

from zope.interface import implementer

from gaphor.core import _, inject, open_action, build_action_group
from gaphor.interfaces import IActionProvider
from gaphor.ui.interfaces import IUIComponent
from gaphor.ui.propertyeditor import PropertyEditor

log = logging.getLogger(__name__)


@implementer(IUIComponent, IActionProvider)
class ElementEditor(object):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    element_factory = inject("element_factory")
    properties = inject("properties")

    title = _("Element Editor")
    size = (275, -1)
    resizable = True
    placement = "floating"
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
        self.property_editor = PropertyEditor()
        self.widget = self.property_editor.construct()

    @open_action(
        name="ElementEditor:open",
        label=_("_Editor"),
        stock_id="gtk-edit",
        accel="<Control>e",
    )
    def open_elementeditor(self):
        """Display the element editor when the toolbar button is toggled.  If
        active, the element editor is displayed.  Otherwise, it is hidden."""

        if not self.widget.get_parent():
            return self

    def open(self):
        """Display and return the PropertyEditor widget."""

        self.widget.show()
        return self.widget

    def close(self):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""

        log.debug("ElementEditor.close")
        # self.action_group.get_action('ElementEditor:open').set_active(False)
        self.widget.unparent()
        # self.dock_item.destroy()
        # return True


# vim:sw=4:et:ai
