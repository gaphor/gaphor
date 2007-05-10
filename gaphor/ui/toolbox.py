"""
Toolbox.
"""

import gobject
import gtk

from gaphor.core import inject

#from gaphor.ui.wrapbox import WrapBox


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

    def __init__(self, menu_factory, toolboxdef):
        """
        Create a new Toolbox instance. Wrapbox objects are generated
        using the menu_factory and based on the toolboxdef definition.
        """
        self.__gobject_init__()
        self.menu_factory = menu_factory
        self.toolboxdef = toolboxdef
        self.boxes = []

    def on_wrapbox_decorator_toggled(self, button, content):
        """
        This function is called when the Wrapbox decorator is clicked. It
        changes the visibility of the content and the arrow in front of the
        button label.
        """
        # Fetch the arrow item:
        arrow = button.get_children()[0].get_children()[0]
        if not content.get_property('visible'):
            content.show()
            arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_IN)
            self.emit('toggled', button.toggle_id, True)
        else:
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

    def new_make_wrapbox_decorator(self, title, content):
        """
        Create a gtk.VBox with in the top compartment a label that can be
        clicked to show/hide the lower compartment.
        """
        expander = gtk.Expander()
        hbox = gtk.HBox()
        expander.set_label_widget(hbox)

        label = gtk.Label(title)
        hbox.pack_start(label, expand=False, fill=False)

        sep = gtk.HSeparator()
        hbox.pack_start(sep, expand=True, fill=True)
        hbox.set_spacing(3)

        expander.add(content)
        
        expanded = self.properties.get('ui.toolbox.%s' % title.replace(' ', '-').lower(), False)
        expander.set_expanded(expanded)

        expander.show_all()
        return expander

    def construct(self):

        self.set_border_width(3)
        vbox = self

        wrapbox_groups = { }
        for title, items in self.toolboxdef:
            wrapbox = self.menu_factory.create_wrapbox(items,
                                                       groups=wrapbox_groups)
            if title:
                wrapbox_dec = self.make_wrapbox_decorator(title, wrapbox)
                vbox.pack_start(wrapbox_dec, expand=False)
                self.boxes.append(wrapbox_dec)
            else:
                vbox.pack_start(wrapbox, expand=False)
                wrapbox.show()
                self.boxes.append(wrapbox)


# vim:sw=4:et:ai
