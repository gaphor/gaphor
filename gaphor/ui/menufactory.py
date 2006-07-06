#/usr/bin/env python
# vim: sw=4:et
"""Handle menus in a MVC manner.

TODO: show tooltips in the status bar when a menu item is selected.
"""

import gobject
import gtk
from gaphor.misc.action import ActionError, Action, CheckAction, RadioAction
from gaphor.misc.action import SlotMenu
#from gaphor.misc.action import get_actions_for_slot
import gaphor.ui.wrapbox

__all__ = [ 'MenuFactory' ]

keyval_map = {
    '+': 'plus',
    '-': 'minus'
}

def _mod_and_keyval_from_accel(accel):
    keyval = 0
    modifier = 0
    if accel:
        gtk_accel = accel.replace('C-', '<Control>').replace('S-', '<Shift>').replace('M-', '<Alt>')
        if gtk_accel[-1] in keyval_map.keys():
            gtk_accel = gtk_accel[:-1] + keyval_map[gtk_accel[-1]]
        keyval, modifier = gtk.accelerator_parse(gtk_accel)
        #log.debug('Translated %s to %d' % (gtk_accel, keyval))

#        accel = accel.upper()
#        if accel.find('S-') != -1:
#            modifier |= gtk.gdk.SHIFT_MASK
#        if accel.find('C-') != -1:
#            modifier |= gtk.gdk.CONTROL_MASK
#        if accel.find('M-') != -1:
#            modifier |= gtk.gdk.MOD1_MASK
#        keyval = ord(accel[-1])
    return modifier, keyval


class MenuFactory(object):
    """This factory is used to create window menus and popup menus.

    On initialization the menu factory can be assigned an accelerator group
    (which will hold key shortcuts for some commands) as well as a statusbar
    and a statusbar_context. The statusbar can be used to display the
    tooltips of the (popup) menu items.

    action_initializer is a function that will be called once a new action
    instance has been created.

    NOTE: When you use GtkWidget.show_all() to show your window, also
    invisible menu items will be shown (this is not desirable). 
    """

    def __init__(self, window_class, action_pool, accel_group=None,
                 statusbar=None, statusbar_context=0):
        self.action_pool = action_pool
        self.in_activation = False
        
        self.accel_group = accel_group
        self.accel_class = window_class + 'Action'
        self.statusbar = statusbar
        self.statusbar_context = statusbar_context
        #self._slot_to_menu_item = {}

    def get_action(self, action_id):
        """Find the action, create a new one if not found.
        If no action is defined with action_id as id, None is returned.
            get_action(action_id) -> Action or None
        """
        try:
            return self.action_pool.get_action(action_id)
        except ActionError:
            return None

    def _create_menu_items(self, menu_def, groups, menu, item=None):
        """Create the items that have to be added to the menu and their
        submenus.
        """
        for id in menu_def:
            if type(id) in (tuple, list):
                # Create and populate a new submenu
                submenu = gtk.Menu()
                submenu.set_accel_group(self.accel_group)
                self._create_menu_items(id, groups, submenu)
                item.set_submenu(submenu)
                submenu.owning_menu_item = item
                self._set_submenu_sensitivity(submenu)
                submenu.show()
            elif id.startswith('<') and id.endswith('>'):
                # We're dealing with a placeholder here, strip the <>
                #slot_def = get_actions_for_slot(id[1:-1])
                #self._create_menu_items(slot_def, groups, menu, item)
                self.create_slot(id[1:-1], menu)
            else:
                item = self.create_menu_item(id, groups)
                menu.add(item)
                self.set_accelerator(id, item)

    def create_menu(self, menu_def):
        """Create a menu bar.
           create_menu(menu_def) -> gtk.Menubar object
        """
        menu = gtk.MenuBar()
        self._create_menu_items(menu_def, { }, menu)

        return menu

    def create_popup(self, menu_def, fire_and_forget=False):
        """Create a popup menu

        create_popup(menu_def[, fire_and_forget]) -> popup menu

        If fire_and_forget == True, the popup menu is destroyed after an
        item was selected.
        """
        menu = gtk.Menu()
        self._create_menu_items(menu_def, { }, menu)
        if fire_and_forget:
            # Make sure the menu is destroyed after it is closed.
            def idle_destroy_menu(data):
                data.destroy()
                return False
            menu.connect('hide', lambda m: gobject.idle_add(idle_destroy_menu, m))
        return menu

    def create_menu_item(self, id, groups=None):
        """Create a MenuItem object, depending on the id given.
        If id is 'separator' or 'tearoff', a separator or tearoff object is
        created. id may also be the id of an action. In this case a menu item
        is created, which depends on the kind of action (normal, check, radio).
        """
        action = self.get_action(id)

        if not action:
            if id == 'separator':
                item = gtk.SeparatorMenuItem()
            elif id == 'tearoff':
                item = gtk.TearoffMenuItem()
            else:
                # We deal with a menu item name
                item = gtk.MenuItem(id)
            item.show()
            return item
        else:
            stock_info = None
            if action.stock_id:
                stock_info = gtk.stock_lookup(action.stock_id)
                # stock_info : (id, label, mod, key, translationdomain)
                try:
                    label = stock_info[1]
                except TypeError:
                    label = action.label
            else:
                label = action.label

            if isinstance(action, RadioAction):
                try:
                    group = groups[action.group]
                except KeyError:
                    group = None
                item = gtk.RadioMenuItem(group, label)
                if not group:
                    groups[action.group] = item
                item.set_active(action.active)
                item.connect('activate', self.on_radio_item_activate, action.id)
                self._connect_item_to_action('notify::active', action, item,
                                            self.on_radio_menu_item_notify_active)
            elif isinstance(action, CheckAction):
                item = gtk.CheckMenuItem(label)
                item.set_active(action.active)
                item.connect('activate', self.on_check_item_activate, action.id)
                self._connect_item_to_action('notify::active', action, item,
                                            self.on_menu_item_notify_action)
            else:
                if action.stock_id:
                    item = gtk.ImageMenuItem(action.stock_id)
                    # stock_info: (id, label, mod, key, translationdomain)
                    # Set the label right
                    item.get_children()[0].set_text_with_mnemonic(label)
                else:
                    item = gtk.MenuItem(label)
                item.connect('activate', self.on_item_activate, action.id)

            # Connect to the event so we can push/pop status messages:
            item.show()
            item.connect('event', self.on_item_event, action.id)
            item.set_property('visible', action.visible)
            item.set_property('sensitive', action.sensitive)
            self._connect_item_to_action('notify::visible', action, item,
                                        self.on_menu_item_notify_action)
            self._connect_item_to_action('notify::sensitive', action, item,
                                        self.on_menu_item_notify_action)
        return item

    def set_accelerator(self, id, item):
        """When available, set an accelerator in the action. This
        is done by creating an accel_path on the item (<window-class>/action.id)
        and defining the accelerator in the global gtk.AccelMap.
        """
        action = self.get_action(id)
        if not action:
            return

        keyval = None
        modifier = None

        #  Fetch accelerator from the stock id.
        if action.stock_id:
            stock_info = gtk.stock_lookup(action.stock_id)
            # stock_info : (id, label, mod, key, translationdomain)
            try:
                keyval = stock_info[3]
                modifier = stock_info[2]
            except TypeError:
                pass

        # Use an accelerator defined in the action class.
        if not keyval and action.accel:
            modifier, keyval = _mod_and_keyval_from_accel(action.accel)

        # No accelerator at all.
        if not keyval:
            return

        accel_path = '<' + self.accel_class + '>/' + id
        item.set_accel_path(accel_path)
        gtk.accel_map_add_entry(accel_path, keyval, modifier)
            
    def create_slot(self, slot_id, menu):
        """Create a slot. A slot can change it's content during the lifetime
        of the application. A handler is connected to the slot's 'rebuild'
        signal, so the menu is rebuild when the content has changed.
        """
        slot_menu = self.action_pool.get_slot(slot_id)
        # Create a menu item that acts as a placeholder:
        item = gtk.MenuItem()
        item.slot_size = 0
        menu.add(item)
        #self._slot_to_menu_item[slot_menu] = item
        #self._connect_item_to_action('rebuild')
        handler = slot_menu.connect('rebuild', self.on_slot_menu_rebuild, item)
        item.connect('destroy', self.on_slot_menu_destroy, slot_menu, handler)

        self.on_slot_menu_rebuild(slot_menu, item)

    def create_toolbar(self, menu_def):
        """Create a Toolbar. items in menu_def should not be nested as
        they are when creating a normal menu.
        """
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        groups = { }
        for id in menu_def:
            action = self.get_action(id)
            if not action:
                if id == 'separator':
                    toolbar.append_space()
                else:
                    toolbar.append_element(gtk.TOOLBAR_CHILD_BUTTON,
                                    None, id, '', '', None,
                                    callback=None,
                                    user_data=None)
            else:
                icon, label = self._get_icon_and_label(action, toolbar.get_icon_size())
                if isinstance(action, RadioAction):
                    try:
                        group = groups[action.group]
                    except KeyError:
                        group = None
                    # TODO: replace with toolbar.insert(item, index (-1=append))
                    item = toolbar.append_element(gtk.TOOLBAR_CHILD_RADIOBUTTON,
                                    None, label, action.tooltip, '', icon,
                                    callback=self.on_radio_item_activate,
                                    user_data=action.id)
                    self._connect_item_to_action('notify::active', action, item,
                                                 self.on_radio_menu_item_notify_active)
                    self.in_activation = True
                    if not group:
                        groups[action.group] = item
                    else:
                        item.set_group(group)
                    item.set_active(action.active)
                    self.in_activation = False
                elif isinstance(action, CheckAction):
                    item = toolbar.append_element(gtk.TOOLBAR_CHILD_TOGGLEBUTTON,
                                    None, label, action.tooltip, '', icon,
                                    callback=self.on_check_item_activate,
                                    user_data=action.id)
                    self._connect_item_to_action('notify::active', action, item,
                                                 self.on_menu_item_notify_action)
                    self.in_activation = True
                    item.set_active(action.active)
                    self.in_activation = False
                else:
                    item = toolbar.append_element(gtk.TOOLBAR_CHILD_BUTTON,
                                    None, label, str(action.tooltip), '', icon,
                                    callback=self.on_item_activate,
                                    user_data=action.id)
                item.set_property('visible', action.visible)
                item.set_property('sensitive', action.sensitive)
                self._connect_item_to_action('notify::visible', action, item,
                                             self.on_menu_item_notify_action)
                self._connect_item_to_action('notify::sensitive', action, item, self.on_menu_item_notify_action)
        return toolbar

    def create_button(self, id, groups=None, tooltips=None):
        """Create a button that suits the action id given. If id is
        'separator', a VSeparator object is created. In all other cases a 
        button is created that fits the action (normal, check or radio button).
        """
        action = self.get_action(id)
        if not action:
            if id == 'separator':
                sep = gtk.VSeparator()
                sep.show()
                return sep
            label = id
            icon = None
            item = gtk.Button()
        else:
            icon, label = self._get_icon_and_label(action)
            if isinstance(action, RadioAction):
                try:
                    group = groups[action.group]
                except KeyError:
                    group = None
                item = gtk.RadioButton(group)
                item.set_mode(False)
                item.connect('toggled', self.on_radio_item_activate, action.id)
                self._connect_item_to_action('notify::active', action, item,
                                             self.on_radio_menu_item_notify_active)
                self.in_activation = True
                if not group:
                    groups[action.group] = item
                #else:
                #    item.set_group(group)
                item.set_active(action.active)
                self.in_activation = False
            elif isinstance(action, CheckAction):
                item = gtk.CheckButton()
                item.set_mode(False)
                item.connect('toggled', self.on_check_item_activate, action.id)
                self._connect_item_to_action('notify::active', action, item,
                                             self.on_menu_item_notify_action)
                self.in_activation = True
                item.set_active(action.active)
                self.in_activation = False
            else:
                #if action.stock_id:
                    #item = gtk.Button(action.stock_id)
                    #item.set_property('use-stock', True)
                #else:
                item = gtk.Button()

            if action.stock_id:
                #item.set_property('stock-id', action.stock_id)
                item.add(icon)
                icon.show()
            else:
                item.set_label(label)
            if tooltips:
                tooltips.set_tip(item, action.tooltip or action.label.replace('_', ''))
            item.set_property('visible', action.visible)
            item.set_property('sensitive', action.sensitive)
            self._connect_item_to_action('notify::visible', action, item,
                                         self.on_menu_item_notify_action)
            self._connect_item_to_action('notify::sensitive', action, item,
                                         self.on_menu_item_notify_action)
            item.show()
            return item

    def create_wrapbox(self, menu_def, groups=None):
        """Create a Wrapbox. items in menu_def should not be nested as
        they are when creating a normal menu.
        """
        wrapbox = gaphor.ui.wrapbox.Wrapbox()
        tooltips = gtk.Tooltips()
        if groups is None:
            groups = { }
        for id in menu_def:
                # TODO: Allow toolbox slots
                #elif id.startswith('<') and id.endswith('>'):
                #    # We're dealing with a placeholder here, strip the <>
                #    slot_def = get_actions_for_slot(id[1:-1])
                #    self._create_menu_items(slot_def, groups, menu, item)
                item = self.create_button(id, groups, tooltips)
                #wrapbox.pack(item, False, False, False, False)
                if item:
                    try:
                        wrapbox.add(item)
                    except TypeError, e:
                        log.error('Could not create item for %s' % id, e)
        tooltips.enable()
        wrapbox.tooltips = tooltips
        return wrapbox

    def on_item_activate(self, menu_item, action_id):
        """Call the action that is associated with the menu item.
        """
        self.action_pool.execute(action_id)

    def on_slot_menu_rebuild(self, slot_menu, slot_item):
        """Rebuild the content of a slot menu in a menu. This is done
        by finding a specific placeholder in the menu and removing all
        contained elements. After that the elements are created again
        based on the action id's obtained from DynamicMenu.get_menu().
        """
        #log.debug('Rebuilding slot %s (%s)' % (slot_menu.slot_id, type(slot_menu)))
        #slot_item = self._slot_to_menu_item[slot_menu]
        menu = slot_item.get_parent()
        children = menu.get_children()
        slot_index = children.index(slot_item) + 1

        # Remove the old menu items:
        if slot_item.slot_size > 0:
            for i in xrange(slot_index, slot_index + slot_item.slot_size):
                children[i].destroy()

        slot_item.slot_size = 0

        # Now create the new items. First create them in a list, then insert
        # them into the menu at the right place.
        groups = {}
        menu_list = FakeMenu()
        self._create_menu_items(slot_menu.get_menu(), groups, menu_list)

        # Add them to the menu
        for item in menu_list:
            menu.insert(item, slot_index)
            slot_index += 1
            slot_item.slot_size += 1
        self._set_submenu_sensitivity(menu)

    def on_menu_item_notify_action(self, menu_item, pspec, action_id):
        """Helper callback, copies state from the action to the menu item.
        """
        #print self, menu_item, pspec, action_id
        menu_item.set_property(pspec.name, self.get_action(action_id).get_property(pspec.name))

    def on_radio_menu_item_notify_active(self, menu_item, pspec, action_id):
        """Helper callback, copies state from the action to the menu item.
        """
        action = self.get_action(action_id)
        if action.active:
            menu_item.set_property('active', action.active)

    def on_check_item_activate(self, menu_item, action_id):
        """Intercept activation of a check menu item. The state is copied
        to the action and the action is executed.
        """
        if self.in_activation: return
        self.in_activation = True
        try:
            action = self.action_pool.get_action(action_id)
            action.active = menu_item.get_property('active')
            self.on_item_activate(menu_item, action_id)
        finally:
            self.in_activation = False

    def on_radio_item_activate(self, menu_item, action_id):
        if self.in_activation: return
        self.in_activation = True
        try:
            active = menu_item.get_property('active')
            self.get_action(action_id).active = active
            if active:
                self.on_item_activate(menu_item, action_id)
        finally:
            self.in_activation = False

    def on_item_event(self, menu_item, event, action_id):
        if self.statusbar:
            if event.type == gtk.gdk.ENTER_NOTIFY:
                tooltip = self.get_action(action_id).tooltip
                #print 'tooltip:', tooltip
                self.statusbar.push(self.statusbar_context, tooltip)
            elif event.type == gtk.gdk.LEAVE_NOTIFY:
                self.statusbar.pop(self.statusbar_context)

    def on_item_destroy(self, menu_item, action_id, handler):
        action = self.get_action(action_id)
        action.disconnect(handler)

    def on_slot_menu_destroy(self, menu_item, slot_menu, handler):
        slot_menu.disconnect(handler)

    def _connect_item_to_action(self, signal_name, action, item, handler):
        """Connect the items signal handler to the action. The handler is
        destroyed when the item is destroyed.
        """
        handler_id = action.connect_object(signal_name, handler, item, action.id)
        item.connect('destroy', self.on_item_destroy, action.id, handler_id)

    def _get_icon_and_label(self, action, icon_size=gtk.ICON_SIZE_LARGE_TOOLBAR):
        if action.stock_id:
            # Fetch stock icon, and probably a text and tooltip:
            stock_info = gtk.stock_lookup(action.stock_id)
            #print stock_info # (id, label, mod, key, translationdomain)
            try:
                label = stock_info[1].replace('_', '')
            except TypeError:
                label = action.label.replace('_', '')
            icon = gtk.Image()
            icon.set_from_stock(action.stock_id, icon_size)
        else:
            label = action.label.replace('_', '')
            icon = None
        return icon, label

    def _set_submenu_sensitivity(self, menu):
        """Determine if a menu entry containing a submenu should
        be sensitive. If the entry contains no (visible) menu items,
        the menu item is made insensitive.
        """
        if not hasattr(menu, 'owning_menu_item'):
            return

        if [ c for c in menu.get_children() if c.get_property('visible')]:
            menu.owning_menu_item.set_property('sensitive', True)
        else:
            menu.owning_menu_item.set_property('sensitive', False)


def toolbox_to_menu(toolbox):
    """Given a toolbox definition, create a list suitable for
    inclusion in a menu.
    """
    l = []
    for box in toolbox:
        if box[0]:
            l.append(box[0])
            l.append(box[1])
        else:
            for item in box[1]:
                l.append(item)
    return l


class FakeMenu(object):

    def __init__(self):
        self.l = []

    def add(self, item):
        self.l.append(item)

    def __iter__(self):
        return self.l.__iter__()
