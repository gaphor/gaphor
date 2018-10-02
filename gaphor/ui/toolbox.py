"""
Toolbox.
"""

import gobject
import gtk

from gaphor.core import inject

from wrapbox import Wrapbox

class Toolbox(gtk.VBox):
    """
    A toolbox is a widget that contains a set of buttons (a Wrapbox widget)
    with a name above it. When the user clicks on the name the box's content
    shows/hides.

    The 'toggled' signal is emited everytime a box shows/hides.

    The toolbox is generated based on a definition with the form:
    ('name', ('boxAction1', 'boxAction2',...), 'name2', ('BoxActionN',...))

    1 Create action pool for placement actions
    2 Create gtk.RadioButtons for each item.
    3 connect to action
    """

    TARGET_STRING = 0
    TARGET_TOOLBOX_ACTION = 1
    DND_TARGETS = [
        ('STRING', gtk.TARGET_SAME_APP, TARGET_STRING),
        ('text/plain', gtk.TARGET_SAME_APP, TARGET_STRING),
        ('gaphor/toolbox-action', gtk.TARGET_SAME_APP, TARGET_TOOLBOX_ACTION)]

    __gsignals__ = {
        'toggled': (gobject.SIGNAL_RUN_FIRST,
                    gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT))
    }

    properties = inject('properties')


    def __init__(self, toolboxdef):
        """
        Create a new Toolbox instance. Wrapbox objects are generated
        using the menu_factory and based on the toolboxdef definition.
        """
        self.__gobject_init__()
        self.buttons = []
        self.shortcuts = {}
        self._construct(toolboxdef)


    def make_wrapbox_decorator(self, title, content):
        """
        Create a gtk.VBox with in the top compartment a label that can be
        clicked to show/hide the lower compartment.
        """
        expander = gtk.Expander()

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
                       icon_size=gtk.ICON_SIZE_LARGE_TOOLBAR):
        button = gtk.ToggleButton()
        button.set_relief(gtk.RELIEF_NONE)
        if stock_id:
            icon = gtk.Image()
            icon.set_from_stock(stock_id, icon_size)
            button.add(icon)
            icon.show()
        else:
            button.props.label = action_name
        button.action_name = action_name
        
        # Enable DND (behaviour like tree view)
        button.drag_source_set(gtk.gdk.BUTTON1_MASK, self.DND_TARGETS,
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
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
                self.pack_start(wrapbox_dec, expand=False)
            else:
                self.pack_start(wrapbox, expand=False)
                wrapbox.show()


    def _button_drag_data_get(self, button, context, selection_data, info, time):
        selection_data.set(selection_data.target, 8, button.action_name)


# vim:sw=4:et:ai
