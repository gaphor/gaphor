# vim:sw=4

import gtk

class MenuItem:

    def __init__(self, name=None, comment='', accel=None,
		 command=None, stock=None, icon=None, submenu=None):
	self.__name = name
	self.__comment = comment
	self.__accel = accel
	self.__command = command
	self.__stock = stock
	self.__icon = icon
	print 'MenuItem.__init__:', submenu
	self.__submenu = submenu

    def get_name(self):
	return self.__name

    def get_comment(self):
	return self.__comment

    def get_accel(self):
	return self.__accel
	
    def get_command(self):
	return self.__command

    def get_stock(self):
	return self.__stock

    def get_icon(self):
	if self.__stock:
	    return None
	return self.__icon

    def get_submenu(self):
	if not self.__submenu:
	    return ()
	return self.__submenu

    def __repr__(self):
	return '<' + str(self.__class__) + ' "' + str(self.__name) + '">'

class MenuSeparator(MenuItem):
    """
    Menu Item for a separator (vertical bar) in the menu.
    """
    def __init__(self):
	MenuItem.__init__(self)


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
	    elif item.get_stock():
		menuitem = gtk.ImageMenuItem(stock_id=item.get_stock(),
					     accel_group=self.__accelgroup)
	    else:
		menuitem = gtk.MenuItem(item.get_name())

	    menu.add(menuitem)

	    # Add a comment
	    comment = item.get_comment()
	    if comment:
		menuitem.connect("select", set_comment_cb, comment)
		menuitem.connect("deselect", unset_comment_cb, comment)

	    # Set the command, if any
	    command = item.get_command()
	    if command:
		menuitem.connect('activate', command_cb, command)

	    if len(item.get_submenu()) > 0:
		submenu = gtk.Menu()
		for subitem in item.get_submenu():
		    create_menu(submenu, subitem)
		menuitem.set_submenu(submenu)

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
	    msg = 'Operation failed'
	sb = self.__statusbar
	if sb:
	    sb.pop()
	    sb.push(str(msg))

    def __handle_set_comment_cb (self, item, comment):
	sb = self.__statusbar
	if sb:
	    sb.push(str(comment))

    def __handle_unset_comment_cb (self, item, comment):
	sb = self.__statusbar
	if sb:
	    sb.pop()

