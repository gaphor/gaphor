# vim: sw=4
"""Command

A command is an object that executes a certain task.
One should inherit from Command and override the execute() and (optionally)
the set_parameters() method.
"""

__version__ = "$Revision$"
__author__ = "Arjan Molenaar"
__date__ = "2002-03-19"

class Command(object):

    def set_parameters (self, params):
	"""Set parameters to be used by the command. By default, this method
	does nothing.
	"""
	pass

    def execute (self):
	"""This method is called to execute the command. The called should
	check if the command may be executed at all by checking is_valid()
	first. This function may return an exception.
	"""
	pass


class StatefulCommand(Command):

    def execute (self, new_state):
	"""Like Command.execute(), however the new state for the command is
	provided as extra parameter."""
	pass
