#/usr/bin/env python
# vim: sw=4:et
"""
"""

import gtk

from gaphor.misc.action import Action, CheckAction, RadioAction, ActionPool, register_action
from gaphor.ui.menufactory import MenuFactory

import weakref

menu_item_refs = []

def connect_weakref(container):
    global menu_item_refs
    for item in container.get_children():
        print 'ref:', item
        menu_item_refs.append(weakref.ref(item))
        if item.get_submenu():
            connect_weakref(item.get_submenu())


class FileNewAction(Action):
    id = 'FileNew'
    stock_id = 'gtk-new'

    def execute(self):
        print 'New'

register_action(FileNewAction)

class FileQuitAction(Action):
    id = 'FileQuit'
    stock_id = 'gtk-quit'
    tooltip = 'Quit the application'

    def execute(self):
        window.destroy()
        #gtk.main_quit()

register_action(FileQuitAction)

class FileCheckAction(CheckAction):
    id = 'FileCheck'
    label = '_Check'
    #stock_id = 'gtk-save'
    tooltip = 'Check the checkbox'

    def execute(self):
        print 'Check', self.active
        action_pool.get_action('FileTest').visible = self.active

register_action(FileCheckAction)

class FileTestAction(Action):
    id = 'FileTest'
    label = '_Test'
    pixname = 'gtk-close'

    def init(self):
        self.visible = 0

    def execute(self):
        self.set_property('visible', 0)
        print 'Test'

register_action(FileTestAction)

class GreenAction(RadioAction):
    id = 'Green'
    label = 'G_reen'
    group = 'color'
    tooltip = 'Makes the world turn green'

    def execute(self):
        print self.label, self.active

register_action(GreenAction)

class YellowAction(RadioAction):
    id = 'Yellow'
    label = 'Yellow'
    group = 'color'
    tooltip = 'Makes the world turn yellow'

    def execute(self):
        print self.label, self.active
        if not self.active:
            import traceback
            traceback.print_stack()

register_action(YellowAction)

class BlueAction(RadioAction):
    id = 'Blue'
    label = 'B_lue'
    group = 'color'
    tooltip = 'Makes the world turn blue'
    
    def execute(self):
        print self.label, self.active

register_action(BlueAction)

class OneAction(RadioAction):
    id = 'One'
    label = 'One'
    group = 'count'
    tooltip = 'Makes the world turn one'
    
    def execute(self):
        print self.label, self.active

register_action(OneAction)

class TwoAction(RadioAction):
    id = 'Two'
    label = 'Two'
    group = 'count'
    tooltip = 'Makes the world turn two'
    
    def execute(self):
        print self.label, self.active

register_action(TwoAction)

class NewRadioAction(RadioAction):
    pass

class StartAction(NewRadioAction):
    id = 'start'
    name = 'middle'
    names = ('start', 'middle', 'end')
    labels = ('Start', 'Middle', 'End')
    stock_ids = ('gtk-open', 'gtk-close', 'gtk-save')

    def execute(self):
        print 'StartAction', self.active

window = gtk.Window()
window.connect('destroy', lambda win: gtk.main_quit())
window.set_title('Menus')

vbox = gtk.VBox()
window.add(vbox)
accel_group = gtk.AccelGroup()
window.add_accel_group(accel_group)

statusbar = gtk.Statusbar()

def init(action):
    try:
        action.init()
    except:
        pass

action_pool = ActionPool(init)
menu_factory = MenuFactory(action_pool, accel_group=accel_group, statusbar=statusbar, statusbar_context=0)
menubar = menu_factory.create_menu(
    ('_File', (
        'tearoff',
        'FileNew',
        'FileTest',
        'FileCheck',
        'separator',
        'FileQuit'),
     '_Edit', (
        'Color', (
            'tearoff',
            'Green',
            'Yellow',
            'Blue'),
        'Count', (
            'tearoff',
            'One',
            'Two'),
        'FileCheck'
        )
    ))

connect_weakref(menubar)

vbox.pack_start(menubar, expand=gtk.FALSE)
menubar.show()

#menu = gtk.Menu()
#new = create_menu_item('_New', '') 
#new = gtk.MenuItem('_New')
#new.add_accelerator('activate', accel_group, ord('n'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
#sep = gtk.SeparatorMenuItem()

toolbar = menu_factory.create_toolbar(('FileNew', 'FileCheck', 'separator', 'Green', 'Yellow', 'Blue'))
handle_box = gtk.HandleBox()
handle_box.add(toolbar)
handle_box.show()
toolbar.show()
vbox.pack_start(handle_box, expand=gtk.FALSE)


def on_event_box_event(event_box, event):
    if event.type == gtk.gdk.BUTTON_PRESS:
        menu = menu_factory.create_popup(('FileCheck',
                                          'separator',
                                          'Green',
                                          'Yellow',
                                          'Blue'))
        connect_weakref(menu)
        menu.popup(None, None, None, event.button, 0)

event_box = gtk.EventBox()
event_box.set_size_request(100, 100)
event_box.connect('event', on_event_box_event)
vbox.pack_start(event_box, expand=gtk.TRUE)

wrap_box = menu_factory.create_wrapbox(('FileNew', 'FileCheck', 'separator', 'Green', 'Yellow', 'Blue'))
vbox.pack_start(wrap_box, expand=gtk.TRUE)
wrap_box.show()

vbox.pack_end(statusbar, expand=gtk.FALSE)
vbox.show()

label = gtk.Label('Press the mouse button here\nto test the popup menu')
label.show()
event_box.add(label)
event_box.show()
window.show()

gtk.main()

del window
del menubar
del event_box
del toolbar

import gc
gc.collect()
gc.collect()

# Check if all items are freed:
for item in menu_item_refs:
    if item():
        print 'Item not freed:', item
