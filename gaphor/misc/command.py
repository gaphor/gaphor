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

    def execute (self, **args):
	"""
	This method is called to execute the command. The called should check
	if the command may be executed at all by checking is_valid() first.
	This function may return an exception.
	"""
	pass

