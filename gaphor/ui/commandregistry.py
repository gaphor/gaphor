# vim:sw=4
"""
The CommandRegistry module contains some code to handle build-in commands.
These commands are registered to the CommandRegistry from which they can be
instantiated and added as commands for the specific menu items.
"""

class _CommandExecuter(object):
    """
    Wrapper class for executing commands from (Bonobo) menus.
    """
    def __init__(self, command):
	self.command = command
	self.executing = 0

    def __call__(self, *args):
	#print 'CommandExecuter.__call__:', args
	if not self.executing:
	    self.executing = 1
	    try:
		self.command.execute()
	    except Exception, e:
		# TODO: create a warning dialog or something
		log.warning('Command execution failed: %s' % e)
		import traceback
		traceback.print_exc()
	    self.executing = 0
	else:
	    log.warning('Cyclic command execution for %s' % self.command)


class CommandRegistry(object):
    """
    One object can contain a bunch of CommandInfo objects. Normally you
    would access this through the GaphorResource() function.
    """

    def __init__(self):
	self.__registry = dict()

    def register(self, command_info):
	if self.__registry.has_key(command_info.context):
	    self.__registry[command_info.context].append(command_info)
	else:
	    self.__registry[command_info.context] = [ command_info ]

    def lookup(self, context, name):
	if self.__registry.has_key(context):
	    for ci in self.__registry[context]:
		if ci.name == name:
		    return ci
	    #return self.__registry[name]
	
    def get_command(self, context, name):
	"""Create a command based on a context and the commands name."""
	cmd_info = self.lookup(context, name)
	if cmd_info and cmd_info.command_class:
	    return cmd_info.command_class()

    def get_command_xml(self, context):
	"""Create a BonoboUI commands XML statement."""
	xml = '<commands>'
	for ctx, infos in self.__registry.items():
	    if ctx.startswith(context):
		for info in infos:
		    xml += info.create_cmd_xml()
	xml += '</commands>'
	return xml

    def get_capabilities(self, context):
	"""Get all names of commands within a context and their capabilities
	in a list of (name, type, capabilities). Type if one of 'state' or
	'sensitive'."""
	caps = list()
	for ctx, infos in self.__registry.items():
	    if ctx.startswith(context):
		for info in infos:
		    if info.sensitive:
			caps.append((info.name, 'sensitive', info.sensitive))
		    if info.state:
			caps.append((info.name, 'state', info.state))
	return caps

    def get_subjects(self, context):
	"""Get a list of (name, element) tuples for all commands within
	the context."""
	subjects = list()
	for ctx, infos in self.__registry.items():
	    if ctx.startswith(context):
		for info in infos:
		    if info.subject:
			subjects.append((info.name, info.subject))
	return subjects
	
    def get_verbs(self, context, params):
	"""Create a list of verbs and a list of listeners.
	Verbs are used for normal menu items. Listeners for statefull menu
	items. A dictionary of parameters can be supplied to the command
	for instantiation.
	This method is called by AbstractWindow to initialize the menus."""
	verbs = list()
	for ctx, infos in self.__registry.items():
	    if ctx.startswith(context):
		for info in infos:
		    try:
			cmd = info.command_class()
			cmd.set_parameters(params)
			if not info.state:
			    verbs.append((info.name, _CommandExecuter(cmd)))
		    except Exception, e:
			print 'No verb created for ' + info.name + ':', e
			import traceback
			traceback.print_exc()
	return verbs

    def get_listeners(self, context, params):
	"""Create a list of verbs and a list of listeners.
	Verbs are used for normal menu items. Listeners for statefull menu
	items. A dictionary of parameters can be supplied to the command
	for instantiation.
	This method is called by AbstractWindow to initialize the menus."""
	#verbs = list()
	listeners = list()
	for ctx, infos in self.__registry.items():
	    if ctx.startswith(context):
		for info in infos:
		    try:
			cmd = info.command_class()
			cmd.set_parameters(params)
			if info.state:
			    listeners.append((info.name, _CommandExecuter(cmd)))
		    except Exception, e:
			print 'No verb created for ' + info.name + ':', e
			import traceback
			traceback.print_exc()
	return listeners

# Register the registry as application wide resource.
GaphorResource(CommandRegistry)

