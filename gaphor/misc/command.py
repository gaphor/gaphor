# vim: sw=4
'''
Command

A command is an object that executes a certain task.
One should inherit from Command and override the execute() and (optionally)
the is_valid() method.
'''

__version__ = "$Revision$"
__author__ = "Arjan Molenaar"
__date__ = "2002-03-19"

class Command(object):

    def __init__(self):
        pass

    def execute (self):
	"""
	This method is called to execute the command. The called should check
	if the command may be executed at all by checking is_valid() first.
	This function may return an exception.
	"""
	pass

    def is_valid (self):
        """
	Tells us if a command is ready to be executed.
	In menu's this method is called when a menu is opened. Non-valid
	commands will be grayed out when the menu appears.
	"""
	return 1
