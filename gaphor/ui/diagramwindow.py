#!/usr/bin/env python
# vim: sw=4

import gtk
import bonobo
import bonobo.ui
from diagramview import DiagramView
import gaphor.config as config
from gaphor import Gaphor

class DiagramWindow(object):
    serial = 1

    def __init__(self):
	self.__diagram = None

    def set_diagram(self, dia):
	if self.__diagram:
	    self.__diagram.disconnect(self.__unlink)
	self.__diagram = dia
	try:
	    self.__window.set_title(dia.name or 'NoName')
	    self.__view.set_diagram(dia)
	except:
	    pass
	if dia:
	    dia.connect(self.__unlink)

    def get_diagram(self):
	return self.__diagram

    def get_view(self):
	return self.__view;

    def get_window(self):
	return self.__window

    def get_ui_component(self):
	return self.__ui_component

    def construct(self):
	if self.__diagram:
	    title = self.__diagram.name or 'NoName'
	else:
	    title = 'NoName'
	window = bonobo.ui.Window ('gaphor.diagram' + str(DiagramWindow.serial),
				   title)
	DiagramWindow.serial += 1

	window.set_size_request(300, 300)
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
	frame.add (view)
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)

	window.set_contents(table)

	window.show_all()
	#window.connect ('destroy', self.__destroy_event_cb)

	# Now set some extra menu items:
	ui_component.set_translate ('/menu/Insert',
	    """
	    <placeholder name=\"InsertElement\">
	      <menuitem name="InsertActor" _label="Actor" verb="InsertActor"/>
	      <menuitem name="InsertUseCase" _label="UseCase" verb="InsertUseCase"/>
	      <menuitem name="InsertClass" _label="Class" verb="InsertClass"/>
	    </placeholder>
	    """)

	self.__view = view
	self.__window = window
	self.__ui_component = ui_component

	# Set commands:
	command_registry = GaphorResource('CommandRegistry')

	ui_component.set_translate ('/', command_registry.create_command_xml(context='diagram.menu'))
	verbs = command_registry.create_verbs(context='diagram.menu',
	                                      params={ 'window': self })

	ui_component.add_verb_list (verbs, None)

    def close(self):
	"""Close the window."""
	self.__window.destroy()
	del self.__window
	del self.__ui_component
	del self.__view
	del self.__diagram

    def __unlink(self, name, dummy1, dummy2):
	if name == '__unlink__':
	    self.window.destroy()
