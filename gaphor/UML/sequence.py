# vim:sw=4

import inspect

class SequenceError(GaphorError):
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
	self.items = []

    def __len__(self):
        return len(self.items)

    def __setitem__(self, key, value):
	raise SequenceError, 'items should not be overwritten.'

    def __delitem__(self, key):
        self.remove(key)

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def __getslice__(self, i, j):
        return self.items.__getslice__(i, j)

    def __setslice__(self, i, j, s):
	raise SequenceError, 'items should not be overwritten.'

    def __delslice__(self, i, j):
	raise SequenceError, 'items should not be deleted this way.'

    def __contains__(self, obj):
        return self.items.__contains__(obj)

    def __iter__(self):
	return iter(self.items)

    def __str__(self):
	return str(self.items)

    def __nonzero__(self):
	return self.items!=[]

    def append(self, obj):
	if isinstance(obj, self.required_type):
	    self.owner.sequence_add(self, obj)
	else:
	    raise SequenceError, 'append(): Object is not of type ' + \
	    			str (self.required_type)

    def remove(self, key):
        self.owner.sequence_remove(self, key)

    def index(self, key):
	"""Given an object, return the position of that object in the sequence.
	"""
	for i in range (0, len (self.items)):
	    if self.items[i] is key:
	        return i
        raise SequenceError, 'index(): key %s not in items' % str(key)
    
    # OCL-like members (from SMW by Ivan Porres
    # (http://www.abo.fi/~iporres/smw))

    def size(self):
        return len(self.items)

    def includes(self,o):
        return o in self.items

    def excludes(self,o):
        return not self.includes(o)

    def count(self,o):
        c=0
        for x in self.items:
            if x==o:
                c=c+1
        return c

    def includesAll(self,c):
        for o in c:
            if o not in self.items:
                return 0
        return 1

    def excludesAll(self,c):
        for o in c:
            if o in self.items:
                return 0
        return 1

    def select(self,f):
        result=list()
        for v in self.items:
            if f(v):
                result.append(v)
        return result

    def reject(self,f):
        result=list()
        for v in self.items:
            if not f(v):
                result.append(v)
        return result

    def collect(self,f):
        result=list()
        for v in self.items:
            result.append(f(v))
        return result

    def isEmpty(self):
        return len(self.items)==0

    def nonEmpty(self):
        return not self.isEmpty()
    
    def sum(self):
        r=0
        for o in self.items:
            r=r+o
        return o
    
    def forAll(self,f):
        if not self.items or not inspect.getargspec(f)[0]:
            return 1

        nargs=len(inspect.getargspec(f)[0])
        if inspect.getargspec(f)[3]:
            nargs=nargs-len(inspect.getargspec(f)[3])
            
        assert(nargs>0)
        nitems=len(self.items)
        index=[0]*nargs
        
        while 1:
            args=[]
            for x in index:
                args.append(self.items[x])
            if not apply(f,args):
                return 0
            c=len(index)-1
            index[c]=index[c]+1
            while index[c]==nitems:
                index[c]=0
                c=c-1
                if c<0:
                    return 1
                else:
                    index[c]=index[c]+1 
                if index[c]==nitems-1:
                    c=c-1

    def exist(self,f):
        if not self.items or not inspect.getargspec(f)[0]:
            return 0

        nargs=len(inspect.getargspec(f)[0])
        if inspect.getargspec(f)[3]:
            nargs=nargs-len(inspect.getargspec(f)[3])
            
        assert(nargs>0)
        nitems=len(self.items)
        index=[0]*nargs
        while 1:
            args=[]
            for x in index:
                args.append(self.items[x])
            if apply(f,args):
                return 1
            c=len(index)-1
            index[c]=index[c]+1
            while index[c]==nitems:
                index[c]=0
                c=c-1
                if c<0:
                    return 0
                else:
                    index[c]=index[c]+1 
                if index[c]==nitems-1:
                    c=c-1
