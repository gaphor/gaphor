#!/usr/bin/env python
# vim: sw=4

import gtk
import bonobo.ui
from diagramview import DiagramView
import gaphor.config as config
from abstractwindow import AbstractWindow

class DiagramWindow(AbstractWindow):
    serial = 1
    
    def __init__(self):
	AbstractWindow.__init__(self)
	self.__diagram = None

    def get_diagram(self):
	return self.__diagram

    def get_view(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__view;

    def set_diagram(self, dia):
	if self.__diagram:
	    self.__diagram.disconnect(self.__on_diagram_event)
	    self.__diagram.canvas.disconnect(self.__undo_id)
	    self.__diagram.canvas.disconnect(self.__snap_to_grid_id)
	self.__diagram = dia
	if self.get_state() == AbstractWindow.STATE_ACTIVE:
	    self.get_window().set_title(dia.name or 'NoName')
	    self.__view.set_diagram(dia)
	if dia:
	    dia.canvas.set_property ('allow_undo', 1)
	    dia.connect(self.__on_diagram_event)
	    self.__undo_id = dia.canvas.connect('undo', self.__on_diagram_undo)
	    # Why doesn't this property react?
	    self.__snap_to_grid_id = dia.canvas.connect('notify::snap_to_grid', self.__on_diagram_notify_snap_to_grid)
	    #dia.canvas.set_property('snap_to_grid', 1)
	    self.__on_diagram_undo(dia.canvas)

    def construct(self):
	self._check_state(AbstractWindow.STATE_INIT)
	#if self.__diagram:
	title = self.__diagram and self.__diagram.name or 'NoName'
	#else:
	#    title = 'NoName'

	DiagramWindow.serial += 1

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

	view.connect('notify::tool', self.__on_view_notify_tool)
	view.connect_after('event', self.__on_view_event)
	view.connect('focus_item', self.__on_view_focus_item)
	view.connect('select_item', self.__on_view_select_item)
	view.connect('unselect_item', self.__on_view_select_item)
	self.__view = view

	self._construct_window(name='diagram',
			       title=title,
			       size=(400, 400),
			       contents=table,
			       params={ 'window': self })

    def _on_window_destroy(self, window):
	"""
	Window is destroyed. Do the same thing that would be done if
	File->Close was pressed.
	"""
	AbstractWindow._on_window_destroy(self, window)
	self.set_diagram(None)
	del self.__view
	del self.__diagram

    def __on_view_notify_tool(self, view, tool):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	#print self, view, tool
	if not view.get_property('tool'):
	    self.set_message('')

    def __on_view_event(self, view, event):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	# handle mouse button 3 (popup menu):
	if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
	    view.canvas.push_undo(None)
	    cmd_reg = GaphorResource('CommandRegistry')
	    verbs = cmd_reg.get_verbs(context='diagram.popup',
				      params={ 'window': self })
	    self.get_ui_component().add_verb_list (verbs, None)
	    menu = gtk.Menu()
	    # The window takes care of destroying the old menu, if any...
	    self.get_window().add_popup(menu, '/popups/DiagramView')
	    menu.popup(None, None, None, event.button, 0)
	    view.stop_emission('event')
	    return True
	return False

    def __on_view_focus_item(self, view, focus_item):
	#log.debug('focus_item %s %s'% (view, focus_item))
	self.set_capability('focus', focus_item is not None)

    def __on_view_select_item(self, view, select_item):
	#log.debug('select_item %s %s %d' % (view, select_item, len(view.selected_items)))
	self.set_capability('select', len (view.selected_items) > 0)

    def __on_diagram_undo(self, canvas):
	self.set_capability('undo', canvas.get_undo_depth() > 0)
	self.set_capability('redo', canvas.get_redo_depth() > 0)

    def __on_diagram_notify_snap_to_grid(self, canvas):
	log.debug('notify:snap_to_grid = %d' % canvas.get_property('snap_to_grid'))
	
	self.set_capability('snap_to_grid', canvas.get_property('snap_to_grid'))

    def __on_diagram_event(self, name, old, new):
	if name == 'name':
	    self.get_window().set_title(new)
	elif name == '__unlink__':
	    self.close()
