# vim: sw=4
'''Command
A command is an object that executes a certain task.
One should inherit from Command and override the execute() method.
'''

__version__ = "$Revision$"
__author__ = "Arjan Molenaar"
__date__ = "2002-03-19"

class Command:

    def __init__(self):
        pass

    def execute (self):
	pass

    def is_valid (self):
        """
	Tells us if a command is reasy to be executed.
	In menu's this method is called when a menu is opened. Non-valid
	commands will be grayed out when the menu appears.
	"""
	return 1
