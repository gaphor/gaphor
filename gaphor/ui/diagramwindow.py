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

    def get_window(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__window

    def get_ui_component(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__ui_component

    def construct(self):
	self._check_state(AbstractWindow.STATE_INIT)
	if self.__diagram:
	    title = self.__diagram.name or 'NoName'
	else:
	    title = 'NoName'
	window = bonobo.ui.Window ('gaphor.diagram' + str(DiagramWindow.serial),
				   title)
	DiagramWindow.serial += 1

	window.set_size_request(400, 400)
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path (config.CONFIG_PATH + '/diagram')
	ui_component = bonobo.ui.Component ('diagram')
	ui_component.set_container (ui_container.corba_objref ())

	bonobo.ui.util_set_ui (ui_component, config.DATADIR,
			       'gaphor-diagram-ui.xml', config.PACKAGE_NAME)

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
	# TEST
	label = gtk.Label('Drop Here!\n')
	#label.drag_dest_set(gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
	view.drag_dest_set(gtk.DEST_DEFAULT_ALL, DiagramView.DND_TARGETS,
			    gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

	def label_drag_data_received(w, context, x, y, data, info, time):
	    try:
		if data and data.format == 8:
		    print 'Received "%s" in label' % data.data
		    context.finish(gtk.TRUE, gtk.FALSE, time)
		else:
		    print 'Received something in label'
		    context.finish(gtk.FALSE, gtk.FALSE, time)
	    except:
	    	pass
	#label.connect('drag_data_received', label_drag_data_received)
	#view.connect('drag_data_received', label_drag_data_received)

	frame.add (view)
	#frame.add(label)
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)

	window.set_contents(table)

	self.__destroy_id = window.connect('destroy', self.__on_window_destroy)
	view.connect('notify::tool', self.__on_view_notify_tool)

	window.show_all()
	#window.connect ('destroy', self.__destroy_event_cb)

	self.__view = view
	self.__window = window
	self.__ui_component = ui_component

	self._set_state(AbstractWindow.STATE_ACTIVE)

	# Set commands:
	command_registry = GaphorResource('CommandRegistry')

	ui_component.set_translate ('/', command_registry.create_command_xml(context='diagram.'))
	verbs = command_registry.create_verbs(context='diagram.menu',
	                                      params={ 'window': self })
	ui_component.add_verb_list (verbs, None)

    def set_diagram(self, dia):
	if self.__diagram:
	    self.__diagram.disconnect(self.__on_diagram_event)
	    self.__diagram.canvas.disconnect(self.__undo_id)
	self.__diagram = dia
	if self.get_state() == AbstractWindow.STATE_ACTIVE:
	    self.__window.set_title(dia.name or 'NoName')
	    self.__view.set_diagram(dia)
	if dia:
	    dia.canvas.set_property ("allow_undo", 1)
	    dia.connect(self.__on_diagram_event)
	    self.__undo_id = dia.canvas.connect("undo", self.__on_diagram_undo)
	    self.__on_diagram_undo(dia.canvas)

    def set_message(self, message):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__ui_component.set_status(message or ' ')

    def close(self):
	"""Close the window."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__window.disconnect(self.__destroy_id)
	self.__window.destroy()
	self._set_state(AbstractWindow.STATE_CLOSED)
	self.set_diagram(None)
	del self.__window
	del self.__ui_component
	del self.__view
	del self.__diagram

    def __on_window_destroy(self, window):
	"""
	Window is destroyed. Do the same thing that would be done if
	File->Close was pressed.
	"""
	self._check_state(AbstractWindow.STATE_ACTIVE)
        cmd_reg = GaphorResource('CommandRegistry')
	cmd = cmd_reg.create_command('FileClose')
	cmd.set_parameters ({ 'window': self })
	cmd.execute()
	self._set_state(AbstractWindow.STATE_CLOSED)

    def __on_view_notify_tool(self, view, tool):
	print self, view, tool
	if not view.get_property('tool'):
	    self.set_message('')

    def __on_diagram_undo(self, canvas):
	self.get_ui_component().set_prop ('/commands/EditUndo', 'sensitive', 
				((canvas.get_undo_depth() > 0) and '1' or '0'))
	self.get_ui_component().set_prop ('/commands/EditRedo', 'sensitive', 
				((canvas.get_redo_depth() > 0) and '1' or '0'))

    def __on_diagram_event(self, name, old, new):
	if name == 'name':
	    self.get_window().set_title(new)
	elif name == '__unlink__':
	    self.close()
