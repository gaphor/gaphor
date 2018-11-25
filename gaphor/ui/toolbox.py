"""
Toolbox.
"""

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor.core import inject
from gaphor.ui.wrapbox import Wrapbox


class Toolbox(Gtk.VBox):
    """
    A toolbox is a widget that contains a set of buttons (a Wrapbox widget)
    with a name above it. When the user clicks on the name the box's content
    shows/hides.

    The 'toggled' signal is emited everytime a box shows/hides.

    The toolbox is generated based on a definition with the form:
    ('name', ('boxAction1', 'boxAction2',...), 'name2', ('BoxActionN',...))

    1 Create action pool for placement actions
    2 Create Gtk.RadioButtons for each item.
    3 connect to action
    """

    TARGET_STRING = 0
    TARGET_TOOLBOX_ACTION = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new('STRING', Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new('gaphor/toolbox-action', Gtk.TargetFlags.SAME_APP, TARGET_TOOLBOX_ACTION)]

    __gsignals__ = {
        'toggled': (GObject.SignalFlags.RUN_FIRST,
                    None, (GObject.TYPE_STRING, GObject.TYPE_INT))
    }

    properties = inject('properties')

    def __init__(self, toolboxdef):
        """
        Create a new Toolbox instance. Wrapbox objects are generated
        using the menu_factory and based on the toolboxdef definition.
        """
        GObject.GObject.__init__(self)
        self.buttons = []
        self.shortcuts = {}
        self._construct(toolboxdef)

    def make_wrapbox_decorator(self, title, content):
        """
        Create a Gtk.VBox with in the top compartment a label that can be
        clicked to show/hide the lower compartment.
        """
        expander = Gtk.Expander()

        expander.set_label(title)

        prop = 'ui.toolbox.%s' % title.replace(' ', '-').lower()
        
        expanded = self.properties.get(prop, False)
        expander.set_expanded(expanded)

        expander.connect('activate', self.on_expander_toggled, prop)

        expander.add(content)

        expander.show_all()

        return expander


    def on_expander_toggled(self, widget, prop):
        # Save the property (inverse value as handler is called before the
        # action takes place):
        self.properties.set(prop, not widget.get_expanded())
        

    def toolbox_button(self, action_name, stock_id,
                       icon_size=Gtk.IconSize.LARGE_TOOLBAR):
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        if stock_id:
            icon = Gtk.Image()
            icon.set_from_stock(stock_id, icon_size)
            button.add(icon)
            icon.show()
        else:
            button.props.label = action_name
        button.action_name = action_name
        
        # Enable DND (behaviour like tree view)
        button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, self.DND_TARGETS,
                Gdk.DragAction.COPY | Gdk.DragAction.LINK)
        button.drag_source_set_icon_stock(stock_id)
        button.connect('drag-data-get', self._button_drag_data_get)

        return button

    def _construct(self, toolboxdef):
        shortcuts = self.shortcuts
        for title, items in toolboxdef:
            wrapbox = Wrapbox()
            for action_name, label, stock_id, shortcut in items:
                button = self.toolbox_button(action_name, stock_id)
                if label:
                    button.set_tooltip_text('%s (%s)' % (label, shortcut))
                self.buttons.append(button)
                wrapbox.add(button)
                button.show()
                shortcuts[shortcut] = action_name
            if title:
                wrapbox_dec = self.make_wrapbox_decorator(title, wrapbox)
                self.pack_start(wrapbox_dec, False, True, 0)
            else:
                self.pack_start(wrapbox, False, True, 0)
                wrapbox.show()

    def _button_drag_data_get(self, button, context, data, info, time):
        """The drag-data-get event signal handler.

        The drag-data-get signal is emitted on the drag source when the drop
        site requests the data which is dragged.

        Args:
            button (Gtk.Button): The button that received the signal.
            context (Gdk.DragContext): The drag context.
            data (Gtk.SelectionData): The data to be filled with the dragged
                data.
            info (int): The info that has been registered with the target in
                the Gtk.TargetList
            time (int): The timestamp at which the data was received.

        """
        data.set(data.get_target(), 8, button.action_name.encode())


# vim:sw=4:et:ai
