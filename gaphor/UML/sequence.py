
class Sequence:
    '''A Sequence class has the following properties:
    - A sequence is an unordered list of unique elements.
    - Only accepts object of a certain type (or descendants).
    - Only keep one reference to the object.
    - A Sequence might have an owner. In that care the owners
      sequence_{add|remove}() functions are called to allow
      bi-directional relations to be added and deleted.'''
    def __init__(self, owner, type):
	self.owner = owner
	self.requested_type = type
	self.list = []

    def __len__(self):
        return self.list.__len__()

    def __setitem__(self, key, value):
	raise Exception, 'Sequence: items should not be overwritten.'

    def __delitem__(self, key):
	if self.owner:
	    self.owner.sequence_remove(self, key)
	else:
            self.list.__delitem__(key)

    def __getitem__(self, key):
        return self.list.__getitem__(key)

    def __getslice__(self, i, j):
        return self.list.__getslice__(i, j)

    def __setslice__(self, i, j, s):
	raise IndexError, 'Sequence: items should not be overwritten.'

    def __delslice__(self, i, j):
	raise IndexError, 'Sequence: items should not be deleted this way.'

    def __contains__(self, obj):
        return self.list.__contains__(obj)

    def append(self, obj):
	if isinstance (obj, self.requested_type):
	    if self.list.count (obj) == 0:
		self.list.append (obj)
		self.list.sort ()
	else:
	    raise ValueError, 'Sequence._add(obj): Object is not of type ' + \
	    			str (self.requested_type)

    def remove(self, key):
        self.__delitem__(key)

    def index(self, key):
        return self.list.index(key)
    
