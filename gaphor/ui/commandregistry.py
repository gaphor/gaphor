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

    def __call__(self, uic, verbname):
	self.command.execute()

class CommandRegistry(object):
    """
    One object can contain a bunch of CommandInfo objects. Normally you
    would access this through the GaphorResource() function.
    """

    def __init__(self):
	self.__registry = dict()

    def register(self, command_info):
	self.__registry[command_info.name] = command_info

    def lookup(self, name):
	if self.__registry.has_key(name):
	    return self.__registry[name]
	
    def values(self):
	return self.__registry.values()

    def create_command(self, name):
	cmd_info = self.lookup(name)
	if cmd_info and cmd_info.command_class:
	    return cmd_info.command_class()

    def create_command_xml(self, context):
	xml = '<commands>'
	for info in self.values():
	    if info.context.startswith(context):
		xml += info.create_cmd_xml()
	xml += '</commands>'
	return xml

    def create_verbs(self, context, params):
	"""
	Create a list of verbs. params is a dictionary of parameters that is
	be supplied to the command in order to instantiate it.
	"""
	verbs = list()
	for info in self.values():
	    if info.context.startswith(context):
		try:
		    cmd = info.command_class()
		    # TODO: Add some sort of capability structure. Based on the
		    # capabilities the parameters set is extended by things
		    # like GaphorResources.
		    cmd.set_parameters(params)
		    verbs.append((info.name, _CommandExecuter(cmd)))
		except Exception, e:
		    print 'No verb created for ' + info.name + ': ' + str(e)
	return verbs

# Register the registry as application wide resource.
GaphorResource(CommandRegistry)

