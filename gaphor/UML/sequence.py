# vim:sw=4

import misc

class SequenceError(misc.GaphorError):
    pass
	
class Sequence:
    '''A Sequence class has the following properties:
    - A sequence is an unordered list of unique elements.
    - Only accepts object of a certain type (or descendants).
    - Only keep one reference to the object.
    - A Sequence has an owner. The owners
      sequence_{add|remove}() functions are called to allow
      bi-directional relations to be added and deleted.
      Note that the Sequence itself does not add items to its list, it
      only invokes the owning object if something needs to be done.'''

    def __init__(self, owner, type):
	self.owner = owner
	self.required_type = type
	self.list = []

    def __len__(self):
        return self.list.__len__()

    def __setitem__(self, key, value):
	raise SequenceError, 'items should not be overwritten.'

    def __delitem__(self, key):
        self.remove(key)

    def __getitem__(self, key):
        return self.list.__getitem__(key)

    def __getslice__(self, i, j):
        return self.list.__getslice__(i, j)

    def __setslice__(self, i, j, s):
	raise SequenceError, 'items should not be overwritten.'

    def __delslice__(self, i, j):
	raise SequenceError, 'items should not be deleted this way.'

    def __contains__(self, obj):
        return self.list.__contains__(obj)

    def append(self, obj):
	if isinstance(obj, self.required_type):
	    self.owner.sequence_add(self, obj)
	else:
	    raise SequenceError, 'append(): Object is not of type ' + \
	    			str (self.required_type)

    def remove(self, key):
        self.owner.sequence_remove(self, key)

    def index(self, key):
	for i in range (0, len (self.list)):
	    if self.list[i] is key:
	        return i
        raise SequenceError, 'index(): key %s not in list' % str(key)
    
