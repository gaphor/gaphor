#!/usr/bin/env python
# vim: sw=4

import gtk, gnome.ui
from diagramview import DiagramView
import gaphor.UML as UML
#import gaphor.diagram as diagram
from gaphor import Gaphor
from gaphor.misc.menufactory import MenuFactory, Menu, MenuItem, MenuStockItem, MenuSeparator
import stock
import command.file, command.diagram
from abstractwindow import AbstractWindow

class DiagramWindow(AbstractWindow):

    def __init__(self, diagram=None):
	self.__diagram = None
	if diagram:
	    self.set_diagram(diagram)

    def set_diagram(self, dia):
	if self.__diagram:
	    self.__diagram.disconnect(self.__unlink)
	self.__diagram = dia
	if dia:
	    dia.connect(self.__unlink)

    def get_diagram(self):
	return self.__diagram

    def __depricated_code():
	win = gtk.Window()
	if dia.name == '':
	    title = 'Unknown'
	else:
	    title = dia.name

	win.set_title (title)
	win.set_default_size (300, 300)
	
	view = DiagramView (canvas=dia.canvas)
	statusbar=gnome.ui.AppBar(has_progress=0, has_status=1,
				  interactivity=gnome.ui.PREFERENCES_USER)

	insert_menu = ()

	items=((stock.STOCK_ACTOR, diagram.ActorItem, 'Actor'),
		(stock.STOCK_CLASS, diagram.ClassItem, 'Class'),
		(stock.STOCK_USECASE, diagram.UseCaseItem, 'UseCase'),
		(stock.STOCK_PACKAGE, diagram.PackageItem, 'Package'),
		(stock.STOCK_COMMENT, diagram.CommentItem, 'Comment'),
		(stock.STOCK_COMMENT_LINE, diagram.CommentLineItem, 'Comment line'),
		(stock.STOCK_ASSOCIATION, diagram.AssociationItem, 'Association'),
		(stock.STOCK_GENERALIZATION, diagram.GeneralizationItem, 'Generalization'),
		(stock.STOCK_DEPENDENCY, diagram.DependencyItem, 'Dependency'))

	for item in items:
	    insert_menu = insert_menu + (MenuStockItem (stock_id=item[0],
						command=command.diagram.PlacementCommand(view, dia, item[1]),
	    					comment='Create new ' + item[2] + ' item'),)

	menu =  Menu(
		    MenuItem(name='_File', submenu=(
			MenuStockItem(stock_id=gtk.STOCK_CLOSE,
				comment='Close current window',
				command=command.file.CloseCommand(win))
			,)),
		    MenuItem(name='_Edit', submenu=(
			MenuStockItem(stock_id=gtk.STOCK_UNDO,
				comment='Undo last change',
				command=command.diagram.UndoCommand(view)),
			MenuStockItem(stock_id=gtk.STOCK_REDO,
				comment='Reapply last undone changes',
				command=command.diagram.RedoCommand(view))
			,)),
		    MenuItem(name='_Insert', submenu=insert_menu)
		    )

	vbox = gtk.VBox(homogeneous=gtk.FALSE)
	win.add (vbox)
	
	accelgroup = gtk.AccelGroup()
	win.add_accel_group(accelgroup)

	menu_factory = MenuFactory(menu=menu, accelgroup=accelgroup,
				   statusbar=statusbar)
	
	menubar = menu_factory.create_menu()

	vbox.pack_start(menubar, gtk.FALSE, gtk.FALSE, 0)

	vbox.pack_end(statusbar, gtk.FALSE, gtk.FALSE, 0)

	table = gtk.Table(2,2, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)
	vbox.pack_end (table)

	frame = gtk.Frame()
	frame.set_shadow_type (gtk.SHADOW_IN)
	table.attach (frame, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	view.set_scroll_region(0, 0, 600, 450)
	frame.add (view)
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)

	win.show_all()
	
	self.window = win
	self.canvasview = view
	self.diagram = dia

	Gaphor().get_main_window().add_window(self, title)

	win.connect("destroy", self.__remove)
	dia.connect(self.__unlink)


    def get_name(self):
    	return 'gaphor.diagram'

    def get_title(self):
	if self.__diagram:
	    return self.__diagram.name or 'NoName'
    	return 'NoName'

    def get_default_size(self):
	return (300, 300)

    def create_contents(self):
	table = gtk.Table(2,2, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)

	frame = gtk.Frame()
	frame.set_shadow_type (gtk.SHADOW_IN)
	table.attach (frame, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	view = DiagramView (diagram=self.__diagram)
	view.set_scroll_region(0, 0, 600, 450)
	frame.add (view)
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)

	self.__view = view
	return table

    def get_ui_xml_file(self):
	return 'gaphor-diagram-ui.xml'

    def __remove(self, win):
	Gaphor().get_main_window().remove_window(self)

    def __unlink(self, name, dummy1, dummy2):
	if name == '__unlink__':
	    self.window.destroy()
