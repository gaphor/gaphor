#/usr/bin/env python
# vim: sw=4:et
"""Handle menus in a MVC manner.

TODO: show tooltips in the status bar when a menu item is selected.
"""

import gobject
import gtk
from gaphor.misc.action import ActionError, Action, CheckAction, RadioAction

#from logilab.aspects.weaver import weaver

__all__ = [ 'MenuFactory' ]


class MenuFactory(object):
    """This factory is used to create window menus and popup menus.

    On initialization the menu factory can be assigned an accelerator group
    (which will hold key shortcuts for some commands) as well as a statusbar
    and a statusbar_context. The statusbar can be used to display the
    tooltips of the (popup) menu items.

    action_initializer is a function that will be called once a new action
    instance has been created.

    NOTE: When you use GtkWidget.show_all() to show your window, also
    invisible menu items will be shown. 
    """

    def __init__(self, action_pool, accel_group=None,
                 statusbar=None, statusbar_context=0):
        self.action_pool = action_pool
        self.in_activation = False
        
        self.accel_group = accel_group
        self.statusbar = statusbar
        self.statusbar_context = statusbar_context

    def get_action(self, action_id):
        """Find the action, create a new one if not found.
        """
        try:
            return self.action_pool.get_action(action_id)
        except ActionError:
            return None

    def on_item_activate(self, menu_item, action_id):
        self.action_pool.execute(action_id)

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

    def create_menu_item(self, id, groups=None):
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
            if action.stock_id:
                stock_info = gtk.stock_lookup(action.stock_id)
                #print stock_info # (id, label, mod, key, translationdomain)
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
                self.connect_item_to_action('notify::active', action, item,
                                            self.on_radio_menu_item_notify_active)

            elif isinstance(action, CheckAction):
                item = gtk.CheckMenuItem(label)
                item.set_active(action.active)
                item.connect('activate', self.on_check_item_activate, action.id)
                self.connect_item_to_action('notify::active', action, item,
                                            self.on_menu_item_notify_action)
            else:
                if action.stock_id:
                    item = gtk.ImageMenuItem(action.stock_id, self.accel_group)
                else:
                    item = gtk.MenuItem(label)
                item.connect('activate', self.on_item_activate, action.id)

            # Connect to the event so we can push/pop status messages:
            item.show()
            item.connect('event', self.on_item_event, action.id)
            item.set_property('visible', action.visible)
            #if not action.visible: item.hide()
            #print 'menu item: visible =', item.get_property('visible')
            item.set_property('sensitive', action.sensitive)
            self.connect_item_to_action('notify::visible', action, item,
                                        self.on_menu_item_notify_action)
            self.connect_item_to_action('notify::sensitive', action, item,
                                        self.on_menu_item_notify_action)
        return item

    def connect_item_to_action(self, signal_name, action, item, handler):
        handler_id = action.connect_object(signal_name, handler, item, action.id)
        item.connect('destroy', self.on_item_destroy, action.id, handler_id)

    def create_menu(self, menu_def, popup=False, groups=None):
        """Create a menu bar.
           create_menu(menu_def) -> gtk.Menubar object
        """
        if not popup:
            menu = gtk.MenuBar()
            groups = { }
        else:
            menu = gtk.Menu()
        item = None

        for id in menu_def:
            if type(id) in (tuple, list):
                #print 'creating submenu for', name
                submenu = self.create_menu(id, True, groups)
                item.set_submenu(submenu)
                submenu.show()
            else:
                item = self.create_menu_item(id, groups)
                menu.add(item)
                #item.show()
        return menu

    def create_popup(self, menu_def, fire_and_forget=False):
        """Create a popup menu

        create_popup(menu_def[, fire_and_forget]) -> popup menu

        If fire_and_forget == True, the popup menu is destroyed after an
        item was selected.
        """
        menu = self.create_menu(menu_def, popup=True, groups={ })
        if fire_and_forget:
            # Make sure the menu is destroyed after it is closed.
            def idle_destroy_menu(data):
                data.destroy()
                return False
            menu.connect('hide', lambda m: gobject.idle_add(idle_destroy_menu, m))
        return menu

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
                if action.stock_id:
                    # Fetch stock icon, and probably a text and tooltip:
                    stock_info = gtk.stock_lookup(action.stock_id)
                    #print stock_info # (id, label, mod, key, translationdomain)
                    try:
                        label = stock_info[1].replace('_', '')
                    except TypeError:
                        label = action.label.replace('_', '')
                    icon = gtk.Image()
                    icon.set_from_stock(action.stock_id, toolbar.get_icon_size())
                else:
                    label = action.label.replace('_', '')
                    icon = None
                if isinstance(action, RadioAction):
                    try:
                        group = groups[action.group]
                    except KeyError:
                        group = None
                    item = toolbar.append_element(gtk.TOOLBAR_CHILD_RADIOBUTTON,
                                    None, label, action.tooltip, '', icon,
                                    callback=self.on_radio_item_activate,
                                    user_data=action.id)
                    self.connect_item_to_action('notify::active', action, item,
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
                    self.connect_item_to_action('notify::active', action, item,
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
                self.connect_item_to_action('notify::visible', action, item,
                                            self.on_menu_item_notify_action)
                self.connect_item_to_action('notify::sensitive', action, item,
                                            self.on_menu_item_notify_action)
        return toolbar

