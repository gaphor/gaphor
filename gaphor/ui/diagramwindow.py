#!/usr/bin/env python
# vim: sw=4

import types, gtk, diacanvas
import gaphor.UML as UML
import gaphor.diagram as diagram
from gaphor.misc.storage import Storage
from placementtool import PlacementTool
import command.file
import command.about
from gaphor.gaphor import Gaphor

[
    EDIT_UNDO,
    EDIT_REDO,
    EDIT_DEL_FOCUSED,
    VIEW_ZOOM_IN,
    VIEW_ZOOM_OUT,
    VIEW_ZOOM_100,
    VIEW_SNAP_TO_GRID,
    ITEM_ADD_ACTOR,
    ITEM_ADD_USECASE,
    ITEM_ADD_PACKAGE,
    ITEM_ADD_COMMENT,
    ITEM_ADD_COMMENT_LINE,
    ITEM_ADD_GENERALIZATION,
    ITEM_ADD_ASSOCIATION,
    ITEM_ADD_DEPENDENCY,
    ITEM_ADD_REALIZATION,
    ITEM_ADD_INCLUDE,
    ITEM_ADD_EXTEND
] = range(18)

class DiagramWindow:

    def __menu_item_cb (self, action, widget):
	view = self.canvasview
	dia = self.diagram

	def set_placement_tool (diagram_type, uml_type):
	    #diagram = view.get_data ('diagram')
	    tool = PlacementTool (dia, diagram_type)
	    view.set_tool (tool)

	print 'Action:', action, gtk.item_factory_path_from_widget(widget), view
	view.canvas.push_undo(None)

	if action == EDIT_UNDO:
	    view.canvas.pop_undo()
	elif action == EDIT_REDO:
	    view.canvas.pop_redo()
	elif action == EDIT_DEL_FOCUSED:
	    # If the item is a composite, remove the parent...
	    item = view.focus_item.item
	    while item and item.flags & diacanvas.COMPOSITE:
	    	item = item.parent
	    if item and item.parent:
		item.parent.remove (item)
	elif action == VIEW_ZOOM_IN:
	    view.set_zoom (view.get_zoom() + 0.1)
	elif action == VIEW_ZOOM_OUT:
	    view.set_zoom (view.get_zoom() - 0.1)
	elif action == VIEW_ZOOM_100:
	    view.set_zoom (1.0)
	elif action == VIEW_SNAP_TO_GRID:
	    snap = view.canvas.get_property ('snap_to_grid')
	    view.canvas.set_property ('snap_to_grid', not snap)

	elif action == ITEM_ADD_ACTOR:
	    set_placement_tool (diagram.ActorItem, UML.Actor)
	elif action == ITEM_ADD_USECASE:
	    set_placement_tool (diagram.UseCaseItem, UML.UseCase)
	elif action == ITEM_ADD_PACKAGE:
	    set_placement_tool (diagram.PackageItem, UML.Package)
	elif action == ITEM_ADD_COMMENT:
	    set_placement_tool (diagram.CommentItem, UML.Comment)
	elif action == ITEM_ADD_COMMENT_LINE:
	    set_placement_tool (diagram.CommentLineItem, None)
	elif action == ITEM_ADD_GENERALIZATION:
	    set_placement_tool (diagram.GeneralizationItem, None)
	elif action == ITEM_ADD_ASSOCIATION:
	    set_placement_tool (diagram.AssociationItem, None)
	#elif action == ITEM_ADD_REALIZATION:
	#    set_placement_tool (diagram.Realization, None)
	elif action == ITEM_ADD_DEPENDENCY:
	    set_placement_tool (diagram.DependencyItem, None)
	#elif action == ITEM_ADD_INCLUDE:
	#    set_placement_tool (diagram.Include, None)
	#elif action == ITEM_ADD_EXTEND:
	#    set_placement_tool (diagram.Extend, None)
	else:
	    print 'This item is not iimplemented yet.'

    __menu_items = (
	( '/_Edit', None, None, 0, '<Branch>' ),
	( '/Edit/_Undo', '<control>Z', __menu_item_cb, EDIT_UNDO ),
	( '/Edit/_Redo', '<control>R', __menu_item_cb, EDIT_REDO ),
	( '/Edit/Delete f_Ocused', None, __menu_item_cb, EDIT_DEL_FOCUSED ),
	( '/_View', None, None, 0, '<Branch>' ),
	( '/View/Zoom _In', None, __menu_item_cb, VIEW_ZOOM_IN ),
	( '/View/Zoom _Out', None, __menu_item_cb, VIEW_ZOOM_OUT ),
	( '/View/_Zoom 100%', None, __menu_item_cb, VIEW_ZOOM_100 ),
	( '/View/sep1', None, None, 0, '<Separator>' ),
	( '/View/_Snap to grid', None, __menu_item_cb, VIEW_SNAP_TO_GRID, '<ToggleItem>' ),
	( '/New _Item', None, None, 0, '<Branch>' ),
	( '/New Item/Actor', None, __menu_item_cb, ITEM_ADD_ACTOR ),
	( '/New Item/Use Case', None, __menu_item_cb,  ITEM_ADD_USECASE ),
	( '/New Item/Package', None, __menu_item_cb,  ITEM_ADD_PACKAGE ),
	( '/New Item/Comment', None, __menu_item_cb,  ITEM_ADD_COMMENT ),
	( '/New Item/Comment Line', None, __menu_item_cb,  ITEM_ADD_COMMENT_LINE ),
	( '/New Item/Generalization', None, __menu_item_cb,  ITEM_ADD_GENERALIZATION ),
	( '/New Item/Association', None, __menu_item_cb,  ITEM_ADD_ASSOCIATION ),
	( '/New Item/Dependency', None, __menu_item_cb,  ITEM_ADD_DEPENDENCY )
#	( '/New Item/Realization', None, __menu_item_cb,  ITEM_ADD_REALIZATION ),
#	( '/New Item/Include', None, __menu_item_cb,  ITEM_ADD_INCLUDE ),
#	( '/New Item/Extend', None, __menu_item_cb,  ITEM_ADD_EXTEND )
    )

    def __init__(self, dia):
	win = gtk.Window()
	if dia.name == '':
	    title = 'Unknown'
	else:
	    title = dia.name

	win.set_title (title)
	win.set_default_size (300, 300)
	
	view = diacanvas.CanvasView (canvas=dia.canvas)

	vbox = gtk.VBox(homogeneous=gtk.FALSE)
	win.add (vbox)
	
	accelgroup = gtk.AccelGroup()
	win.add_accel_group(accelgroup)

	item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', accelgroup)
	
	item_factory.create_items(DiagramWindow.__menu_items, self)
	print 'item_factory:', item_factory.get_item('/File'), len(DiagramWindow.__menu_items)

	menubar = item_factory.get_widget('<main>')
	print 'item_factory:', menubar
	vbox.pack_start(menubar, gtk.FALSE, gtk.FALSE, 0)

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
	self.item_factory = item_factory

	Gaphor().get_main_window().add_window(self, title)

	win.connect("destroy", self.__remove)

    def __remove(self, win):
	Gaphor().get_main_window().remove_window(self)
