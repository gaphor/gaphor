# vim:sw=4

import exceptions

class GaphorError(exceptions.Exception):
    def __init__(self, args=None):
	self.args = args

