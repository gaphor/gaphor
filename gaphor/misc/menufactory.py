# vim:sw=4

import gtk


class BaseMenuItem:

    def __init__(self, comment=None, command=None, submenu=None):
	self.__comment = comment
	self.__command = command
	self.__submenu = submenu

    def get_comment(self):
	return self.__comment

    def get_command(self):
	return self.__command

    def get_submenu(self):
	if not self.__submenu:
	    return ()
	return self.__submenu


class MenuItem(BaseMenuItem):

    def __init__(self, name=None, comment=None, accel=None,
		 command=None, submenu=None):
	BaseMenuItem.__init__(self, comment, command, submenu)
	self.__name = name
	self.__accel = accel

    def get_name(self):
	return self.__name

    def get_accel(self):
	return self.__accel
	

class MenuStockItem(BaseMenuItem):

    def __init__(self, stock_id, comment=None, command=None, submenu=None):
	BaseMenuItem.__init__(self, comment, command, submenu)
	self.__stock_id = stock_id

    def get_stock_id(self):
	return self.__stock_id


class MenuPlaceholder(BaseMenuItem):

    def __init__(self, comment=None, is_numbered=0):
	BaseMenuItem.__init__(self, comment)
	self.__is_numbered = is_numbered
	self.__placeholder = None
	self.__entries = []

    def set_placeholder(self, placeholder):
	self.__placeholder = placeholder

    def add(self, key, name, command):
	menu = self.__placeholder.parent
	if menu:
	    index=menu.get_children().index(self.__placeholder)
	    self.__placeholder.hide()
	    menuitem = gtk.MenuItem(name)
	    menu.insert(menuitem, index)
	    menuitem.show()
	    self.__entries.append ((key, name, command, menuitem))
	
    def remove(self, key):
	entry = self.__find_by_key(key)
	entry[3].destroy()
	self.__entries.remove(entry)
	if len (self.__entries) < 1:
	    self.__placeholder.show()

    def __find_by_key(self, key):
	for e in self.__entries:
	    if e[0] == key:
		return e

class MenuSeparator:
    """
    Menu Item for a separator (vertical bar) in the menu.
    """
    def __init__(self):
	pass


class MenuFactory:

    def __init__(self, menu=None, accelgroup=None, statusbar=None):
	self.__menu = menu
	self.__accelgroup = accelgroup
	self.__statusbar = statusbar
	
    def set_accelgroup(self, accelgroup):
	self.__accelgroup = accelgroup

    def set_menu(self, menu):
	delf.__menu = menu

    def set_statusbar(self, statusbar):
	self.__statusbar = statusbar

    def create_menu(self):

	command_cb = self.__handle_command_cb
	set_comment_cb = self.__handle_set_comment_cb
	unset_comment_cb = self.__handle_unset_comment_cb

	def create_menu(menu, item):
	    if isinstance(item, MenuSeparator):
		menuitem = gtk.SeparatorMenuItem()
	    elif isinstance(item, MenuPlaceholder):
		menuitem = gtk.MenuItem('<empty>')
		menuitem.set_sensitive(0)
		item.set_placeholder(menuitem)
	    elif isinstance(item, MenuStockItem):
		menuitem = gtk.ImageMenuItem(stock_id=item.get_stock_id(),
					     accel_group=self.__accelgroup)
	    elif isinstance(item, MenuItem):
		menuitem = gtk.MenuItem(item.get_name())
	    else:
	        raise Exception, "Unknown menu item type %s" % item

	    menu.add(menuitem)

	    if isinstance (item, BaseMenuItem):
		# Set the command, if any
		command = item.get_command()
		if command:
		    menuitem.connect('activate', command_cb, command)

		# Add a comment
		comment = item.get_comment()
		if comment:
		    menuitem.connect("select", set_comment_cb, comment)
		    menuitem.connect("deselect", unset_comment_cb, comment)

		if len(item.get_submenu()) > 0:
		    submenu = gtk.Menu()
		    subitem = gtk.TearoffMenuItem()
		    subitem.show()
		    submenu.add(subitem)
		    for subitem in item.get_submenu():
			create_menu(submenu, subitem)
		    menuitem.set_submenu(submenu)
		    print 'Children:', submenu.get_children()

	    menuitem.show()

	menubar = gtk.MenuBar()
	for item in self.__menu.get_submenu():
	    create_menu(menubar, item)
	menubar.show()
	return menubar

    def __handle_command_cb (self, item, command):
	print item, command
	try:
	    if command.is_valid():
		msg = command.execute()
	except Exception, e:
	    msg = 'Operation failed: ' + str(e)
	sb = self.__statusbar
	if sb and sb.flags() & gtk.REALIZED:
	    sb.pop()
	    sb.push(str(msg or ''))

    def __handle_set_comment_cb (self, item, comment):
	sb = self.__statusbar
	if sb:
	    sb.push(str(comment))

    def __handle_unset_comment_cb (self, item, comment):
	sb = self.__statusbar
	if sb:
	    sb.pop()

