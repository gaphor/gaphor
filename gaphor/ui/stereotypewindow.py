
# vim:sw=4:et

import gobject
import gtk
import gaphor
import gaphor.UML as UML
from abstractwindow import AbstractWindow
from gaphor.i18n import _

def create_option_menu(options):
    menu = gtk.Menu()
    for str in options:
        menu_item = gtk.MenuItem(str)
        menu_item.show()
    gtk.MenuShell.append(menu, menu_item)

    option_menu = gtk.OptionMenu()
    option_menu.set_menu(menu)

    return option_menu


class StereotypeWindow(object):
    """The stereotype window is used to define and describe stereotypes.
    """

    #menu = ('_File', (
		#'FileClose',)
	    #)
	    

    def __init__(self):
        #AbstractWindow.__init__(self)
        pass

    def __text_box(self):
        source = gtk.TextView()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled_window.add(source)

        return scrolled_window, source

    def run(self, window=None):
	hbox = gtk.HBox()

	stereotypes = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
	st_view = gtk.TreeView(stereotypes)
	st_frame = gtk.Frame(_('Stereotypes'))
	st_frame.set_shadow_type(gtk.SHADOW_IN)
	st_frame.add(st_view)
	hbox.add(st_frame)

	vbox = gtk.VBox()

	hbox.pack_start(vbox)

        label = gtk.Label(_('Base class:'))
        vbox.pack_start(label, expand=False, fill=False)
        sc_win = gtk.Entry()
        vbox.pack_start(sc_win, expand=True, fill=True)

        label = gtk.Label(_('Description:'))
        vbox.pack_start(label, expand=False, fill=False)
        sc_win, text_view = self.__text_box()
        vbox.pack_start(sc_win, expand=True, fill=True)

        label = gtk.Label(_('Constraints:'))
        vbox.pack_start(label, expand=False, fill=False)
        sc_win, text_view = self.__text_box()
        vbox.pack_start(sc_win, expand=True, fill=True)

        bbox = gtk.HButtonBox()
        bbox.set_border_width(5)
        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        bbox.add(gtk.Button(stock='gtk-save'))
        bbox.add(gtk.Button(stock='gtk-add'))
        bbox.add(gtk.Button(stock='gtk-delete'))
        vbox.pack_start(bbox, expand=False, fill=False)

	hbox.show_all()

        dialog = gtk.Dialog("Stereotypes", window, 0,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK,))
                            #gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        dialog.vbox.pack_start(hbox, gtk.TRUE, gtk.TRUE, 0)

        response = dialog.run()

        #if response == gtk.RESPONSE_OK:

        dialog.destroy()
