
# vim:sw=4

import bonobo.ui

import gaphor.config as config
from gaphor.misc.signal import Signal
from menufactory import MenuFactory

class WindowFactory(object):
    """
    Factory used for creating GUI windows. Gaphor windows are based on the
    Bonobo.ui.Window class. The factory keeps reference
    """

    def __init__(self):
	self.__windows = list()
	self.__shells = dict()
	self.__signal = Signal()
    
    def create(self, type):
	shell = type()
	name = shell.get_name()
	title = shell.get_title()
	size = shell.get_default_size()
	assert len(size) == 2
	contents = shell.create_contents()
	xml_file = shell.get_ui_xml_file()
	
	window = bonobo.ui.Window (name, title)
	window.show_all ()

	window.set_size_request(size[0], size[1])

	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	engine = window.get_ui_engine ()
	engine.config_set_path ('/gaphor/UIConfig/kvps')
	ui_component = bonobo.ui.Component (name)
	ui_component.set_container (ui_container.corba_objref ())

	if xml_file:
	    bonobo.ui.util_set_ui (ui_component, config.DATADIR,
				   xml_file, config.PACKAGE_NAME)

	verbs = GaphorResource(MenuFactory).create_verbs()
	ui_component.add_verb_list (verbs, None)

	window.set_contents(contents)
	contents.show_all()

	window.connect ('destroy', self.__destroy_event_cb)

	self.__shells[window] = shell

	return window

    def get_shell(self, window):
	try:
	    return self.__shells[window]
	except KeyError:
	    return None

    def __destroy_event_cb(self, window):
	del self.__shells[window]

