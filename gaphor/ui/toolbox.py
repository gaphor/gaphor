# vim:sw=4:et

"""Toolbox.
"""

import gobject
import gtk

from gaphor import resource

# Import this module to ensure actions refered to in the toolbox are loaded
import gaphor.diagram.placementactions

class Toolbox(gtk.VBox):
    
    __gsignals__ = {
        'toggled': (gobject.SIGNAL_RUN_FIRST,
                    gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT))
    }

    def __init__(self, menu_factory, toolboxdef):
        self.__gobject_init__()
        self.menu_factory = menu_factory
        self.toolboxdef = toolboxdef
        self.boxes = []

    def on_wrapbox_decorator_toggled(self, button, content):
        """This function is called when the Wrapbox decorator is clicked. It
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
        resource.set('ui.toolbox.%s' % button.toggle_id,
                     content.get_property('visible'), persistent=True)

    def make_wrapbox_decorator(self, title, content):
        """Create a gtk.VBox with in the top compartment a label that can be
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

        vbox.show_all()

        button.connect('clicked', self.on_wrapbox_decorator_toggled, content)

        vbox.pack_start(content, True, True)
        
        vbox.label = label
        vbox.content = content

        expanded = resource('ui.toolbox.%s' % button.toggle_id, False)
        content.set_property('visible', not expanded)
        self.on_wrapbox_decorator_toggled(button, content)

        return vbox

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

gobject.type_register(Toolbox)

