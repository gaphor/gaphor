# vi:sw=4:et

import inspect

class CollectionError(Exception):
    pass

class collection(object):

    def __init__(self, property, object, type):
        self.property = property
        self.object = object
        self.type = type
        self.items = []

    def __len__(self):
        return len(self.items)

    def __setitem__(self, key, value):
        raise CollectionError, 'items should not be overwritten.'

    def __delitem__(self, key):
        self.remove(key)

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def __getslice__(self, i, j):
        return self.items.__getslice__(i, j)

    def __setslice__(self, i, j, s):
        raise CollectionError, 'items should not be overwritten.'

    def __delslice__(self, i, j):
        raise CollectionError, 'items should not be deleted this way.'

    def __contains__(self, obj):
        return self.items.__contains__(obj)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return str(self.items)

    __repr__ = __str__

    def __nonzero__(self):
        return self.items!=[]

    def append(self, value):
        if isinstance(value, self.type):
            self.property._set(self.object, value)
        else:
            raise CollectionError, 'Object is not of type %s' % self.type.__name__

    def remove(self, value):
        if value in self.items:
            self.property.__delete__(self.object, value)
        else:
            raise AttributeError, '%s not in collection' % value

    def moveUp(self, value):
        items = self.items
        i = items.index(value)
        i = i - 1
        if i >= 0:
            items.remove(value)
            items.insert(i, value)
        # Send a notification that this list has changed
        self.property.notify(value)

    def index(self, key):
        """Given an object, return the position of that object in the
        collection."""
        return self.items.index(key)
    
    # OCL members (from SMW by Ivan Porres, http://www.abo.fi/~iporres/smw)

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
            return True

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
                return False
            c=len(index)-1
            index[c]=index[c]+1
            while index[c]==nitems:
                index[c]=0
                c=c-1
                if c<0:
                    return True
                else:
                    index[c]=index[c]+1 
                if index[c]==nitems-1:
                    c=c-1
	return False

    def exist(self,f):
        if not self.items or not inspect.getargspec(f)[0]:
            return False

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
                return True
            c=len(index)-1
            index[c]=index[c]+1
            while index[c]==nitems:
                index[c]=0
                c=c-1
                if c<0:
                    return False
                else:
                    index[c]=index[c]+1 
                if index[c]==nitems-1:
                    c=c-1
	return False
