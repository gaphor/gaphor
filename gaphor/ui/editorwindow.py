#!/usr/bin/env python
# vim: sw=4

import sys
import gtk
import bonobo.ui
import gaphor.config as config
from abstractwindow import AbstractWindow

class EditorWindow(AbstractWindow):
    
    def __init__(self):
	AbstractWindow.__init__(self)

    def get_window(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__window

    def get_ui_component(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__ui_component

    def get_source_text_view(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__source

    def get_result_text_view(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	return self.__result

    def construct(self):
	self._check_state(AbstractWindow.STATE_INIT)
	window = bonobo.ui.Window ('gaphor.editor',
				   'Gaphor Editor')

	window.set_size_request(400, 400)
	window.set_resizable(True)

	ui_container = window.get_ui_container ()
	ui_engine = window.get_ui_engine ()
	ui_engine.config_set_path (config.CONFIG_PATH + '/editor')
	ui_component = bonobo.ui.Component ('editor')
	ui_component.set_container (ui_container.corba_objref ())

	bonobo.ui.util_set_ui (ui_component, config.DATADIR,
			       'gaphor-editor-ui.xml', config.PACKAGE_NAME)

	table = gtk.Table(3,1, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)

	source = gtk.TextView()
	scrolled_window = gtk.ScrolledWindow()
	scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
	scrolled_window.add(source)

	table.attach (scrolled_window, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	sep = gtk.HSeparator()
	table.attach (source, 0, 1, 1, 2,
		      gtk.FILL | gtk.SHRINK,
		      gtk.FILL | gtk.SHRINK)

	result = gtk.TextView()
	scrolled_window = gtk.ScrolledWindow()
	scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
	scrolled_window.add(result)
	table.attach (scrolled_window, 0, 1, 2, 3,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)

	window.set_contents(table)

	self.__destroy_id = window.connect('destroy', self.__on_window_destroy)

	window.show_all()
	#window.connect ('destroy', self.__destroy_event_cb)

	self.__source = source
	self.__result = result
	self.__window = window
	self.__ui_component = ui_component

	self._set_state(AbstractWindow.STATE_ACTIVE)

	# Set commands:
	command_registry = GaphorResource('CommandRegistry')

	ui_component.set_translate ('/', command_registry.create_command_xml(context='editor.'))
	verbs = command_registry.create_verbs(context='editor.menu',
	                                      params={ 'window': self,
					      	       'source': source,
						       'result': result })
	ui_component.add_verb_list (verbs, None)

    def run(self):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	orig_stdout = sys.stdout
	orig_stderr = sys.stderr
	result_buf = self.get_result_text_view().get_buffer()
	sys.stdout = PseudoFile(result_buf, 'stdout')
	sys.stderr = PseudoFile(result_buf, 'stderr')
	try:
	    text_buf = self.get_source_text_view().get_buffer()
	    text = text_buf.get_text (text_buf.get_start_iter(),
	    			      text_buf.get_end_iter(), 0)

	    code = None
	    try:
		code = compile(text, '<input>', 'exec')
	    except (SyntaxError, OverflowError, ValueError):
	        print 'Error'
	    if code:
		exec code
	except Exception, e:
	    import traceback
	    print 'ERROR: ',
	    traceback.print_exc()
	sys.stdout = orig_stdout
	sys.stderr = orig_stderr

    def set_message(self, message):
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__ui_component.set_status(message or ' ')

    def close(self):
	"""Close the window."""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self.__window.destroy()
	self._set_state(AbstractWindow.STATE_CLOSED)

    def __on_window_destroy(self, window):
	"""
	Window is destroyed. Do the same thing that would be done if
	File->Close was pressed.
	"""
	self._check_state(AbstractWindow.STATE_ACTIVE)
	self._set_state(AbstractWindow.STATE_CLOSED)
	del self.__window
	del self.__ui_component
	del self.__source
	del self.__result


class PseudoFile:

    def __init__(self, text_buffer, tags):
        self.text_buffer = text_buffer
        self.tags = tags

    def write(self, s):
        #self.shell.write(s, self.tags)
	try:
	    tb = self.text_buffer
	    tb.insert(tb.get_end_iter(), s)
	except Exception, e:
	    pass
	while gtk.events_pending():
	    gtk.main_iteration(False)

    def writelines(self, l):
        map(self.write, l)

    def flush(self):
        pass

    def isatty(self):
        return 1

