# vim:sw=4
'''
MenuFactory

This is the factory used to create menus and toolbars. MenuEntry's should
register themselves in the factory. A menu or toolbar is generated based on
a XML file.
'''
from gaphor.misc.observer import Subject
import copy

class MenuEntry(Subject):

    def __init__(self, name, command_class=None, extra_args=None):
	"""name: name of the command (verb name)
	command_class: class to instantiate for the menu
	extra_args: a dictionaty of name-value pairs to be used as extra
		    arguments for command creation.
	"""
	if not name: raise ValueError, 'name may not be None'
	self._name = name
	self._command_class = command_class
	self._extra_args = extra_args

    def get_name(self):
	return self._name

    def get_command_class(self):
	return self._command_class

    def create_command(self, **args):
	print self._command_class
	cmd = None
	if self._extra_args:
	    ea = copy.copy(args)
	    for n, v in self._extra_args.items():
	    	ea[n] = v
	    cmd = self._command_class(**ea)
	else:
	    cmd = self._command_class(**args)
	return cmd

    # read only properties:
    name = property (get_name, None, None, 'Name of the menu entry')
    command_class = property (get_command_class, None, None, 'Command to be executed')



class MenuCommandExecuter(object):
    """
    Wrapper class for executing commands from (Bonobo) menus.
    """
    def __init__(self, command):
	self.command = command

    def __call__(self, uic, verbname):
	self.command.execute()



class MenuFactory(object):

    def __init__(self):
	self.__entries = dict()

    def register(self, menu_entry):
	if not isinstance (menu_entry, MenuEntry):
	    raise TypeError, 'menu_entry can only be of type MenuEntry'

	name = menu_entry.get_name()
	if self.__entries.has_key(name):
	    raise ValueError, 'There is already an action named %s' % name

	self.__entries[name] = menu_entry

    def create_verbs(self, **args):
	"""
	Create a list of (verb-action) tupples. These are used by UICompoments
	to add commands to the menu entries. args is a dict of arguments that
	can be send to the commands. Commands need to find out for themselves
	which arguments they should use.
	"""
	verbs = list()
	for name, value in self.__entries.items():
	    try:
		cmd = value.create_command(**args)
		if cmd:
		    verbs.append((name, MenuCommandExecuter(cmd)))
	    except Exception, e:
		print 'No verb created for', name
	return verbs

