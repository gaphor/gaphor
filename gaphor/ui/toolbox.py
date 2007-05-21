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
        self.toolboxdef = toolboxdef
        #self.boxes = []
        self.buttons = []
        self._construct()

    def on_wrapbox_decorator_toggled(self, button, content):
        """
        This function is called when the Wrapbox decorator is clicked. It
        changes the visibility of the content and the arrow in front of the
        button label.
        """
        # Fetch the arrow item:
        arrow = button.get_children()[0].get_children()[0]
        if not content.get_property('visible'):
            log.debug('switched to visible: %s' % button.toggle_id)
            content.show()
            arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_IN)
            self.emit('toggled', button.toggle_id, True)
        else:
            log.debug('switched to hidden: %s' % button.toggle_id)
            content.hide()
            arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_IN)
            self.emit('toggled', button.toggle_id, False)
        # Save the property:
        self.properties.set('ui.toolbox.%s' % button.toggle_id,
                            content.get_property('visible'))

    def make_wrapbox_decorator(self, title, content):
        """
        Create a gtk.VBox with in the top compartment a label that can be
        clicked to show/hide the lower compartment.
        """
        vbox = gtk.VBox()

        button = gtk.Button()
        button.set_relief(gtk.RELIEF_NONE)
        button.toggle_id = title.replace(' ', '-').lower()
        hbox = gtk.HBox()
        button.add(hbox)

        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_IN)
        hbox.pack_start(arrow, False, False, 0)

        label = gtk.Label(title)
        hbox.pack_start(label, expand=False, fill=False)

        sep = gtk.HSeparator()
        hbox.pack_start(sep, expand=True, fill=True)
        hbox.set_spacing(3)

        vbox.pack_start(button, False, False, 1)
        vbox.pack_start(content, False, False, 1)

        vbox.show_all()

        button.connect('clicked', self.on_wrapbox_decorator_toggled, content)

        vbox.label = label
        vbox.content = content

        expanded = self.properties.get('ui.toolbox.%s' % button.toggle_id, False)
        content.set_property('visible', not expanded)
        self.on_wrapbox_decorator_toggled(button, content)

        return vbox

    def toolbox_button(self, action_name, stock_id,
                       icon_size=gtk.ICON_SIZE_LARGE_TOOLBAR):
        button = gtk.ToggleButton()
        if stock_id:
            icon = gtk.Image()
            icon.set_from_stock(stock_id, icon_size)
            button.add(icon)
            icon.show()
        else:
            button.props.label = action_name
        button.action_name = action_name
        return button

    def _construct(self):

        self.set_border_width(3)

        self.tooltips = gtk.Tooltips()

        for title, items in self.toolboxdef:
            wrapbox = Wrapbox()
            action = None
            for action_name, label, stock_id in items:
                button = self.toolbox_button(action_name, stock_id)
                if label:
                    self.tooltips.set_tip(button, label)
                self.buttons.append(button)
                wrapbox.add(button)
            if title:
                wrapbox_dec = self.make_wrapbox_decorator(title, wrapbox)
                self.pack_start(wrapbox_dec, expand=False)
            else:
                self.pack_start(wrapbox, expand=False)
                wrapbox.show()

        self.tooltips.enable()

# vim:sw=4:et:ai
