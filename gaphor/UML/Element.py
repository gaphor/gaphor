# vim: sw=4
#
# Base class for all UML model objects
#

import types, copy

# Some default types as defined in the MetaModel.
class Integer(int): pass
class UnlimitedInteger(long): pass
class Boolean(int): pass
class String(str): pass
class Name(String): pass
class Expression(String): pass
class LocationReference(String): pass
# Don't know what to do with this one:
Geometry = types.ListType

FALSE = 0
TRUE = not FALSE

class Enumeration_:
    '''The Enumerration class is an abstract class that can be used to create
    enumerated types. One should inherit from Enumeration and define a variable
    '_values' at class level, which holds a list of valid values for the class.
    '''
    def __init__(self):
        self.v = self._values[0]
    def __setattr__(self, key, value):
        if key == 'v' and value in self._values:
	    self.__dict__['v'] = value
	else:
	    raise AttributeError, "Value '" + str(value) + "' is an invalid enumeration type."

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
	raise Exception, "Sequence: items should not be overwritten."

    def __delitem__(self, key):
	if self.owner:
	    self.owner.sequence_remove(self, obj)
	else:
            self.list.__delitem__(key)

    def __getitem__(self, key):
        return self.list.__getitem__(key)

    def __getslice__(self, i, j):
        return self.list.__getslice__(i, j)

    def __setslice__(self, i, j, s):
	raise Exception, "Sequence: items should not be overwritten."

    def __delslice__(self, i, j):
	raise Exception, "Sequence: items should not be deleted this way."

    def __contains__(self, obj):
        return self.list.__contains__(obj)

    def append(self, obj):
	if isinstance (obj, self.requested_type):
	    if self.list.count(obj) == 0:
		self.list.append(obj)
	else:
	    raise ValueError, "Sequence._add(obj): Object is not of type " + \
	    			str(self.requested_type)

    def remove(self, key):
        self.__delitem__(key)

    def index(self, key):
        return self.list.index(key)
    

if __name__ == '__main__':
    print "\n============== Starting Sequence tests... ============\n"

# End of Sequence tests

#
# Base class for all UML model objects
#
# A word on the <class>._attrdef structure:
# The <class>._attrdef structures are dictionaries decribing the
# attributes that may be added to an object of that class.
# Since a lot of objects have di-directional relations with other objects we
# have to create those maps.
# A record consists of two or three fields:
# 1. The default value of the attribute (e.g. "NoName") or a reference to the
#    Sequence class in case of a 0..* relationship.
# 2. Type of object that way be added.
# 3. In case of bi-directional relationships the third argument is the name
#    by which the object is known on the other side.
#

class Element:
    '''Element is the base class for *all* UML MetaModel classes. The
attributes and relations are defined by a <class>._attrdef structure.
A class does not need to define any local variables itself: Element will
retrieve all information from the _attrdef structure.'''
    _attrdef = { }
    def __init__(self, id):
	self.__dict__["_Element__id"] = id

    def __get_attr_info(self, key, klass):
        '''Find the record for 'key' in the <class>._attrdef map.'''
	done = [ ]
	def real_get_attr_info(key, klass):
	    if klass in done:
	        return None
	    done.append(klass)
	    dict = klass._attrdef
	    #print "Checking " + klass.__name__
	    if dict.has_key(key):
		return dict[key]
	    else:
		for base in klass.__bases__:
		    rec = real_get_attr_info(key, base)
		    if rec is not None:
			return rec
	rec = real_get_attr_info(key, klass)
	if rec is None:
	    raise AttributeError, "Attribute " + key + \
		      " is not in class " + self.__class__.__name__
	else:
	    return rec

    def __getattr__(self, key):
	if key == "id":
	    return self.__dict__["_Element__id"]
	elif self.__dict__.has_key(key):
	    # Key is already in the object
	    return self.__dict__[key]
	else:
	    rec = self.__get_attr_info (key, self.__class__)
	    if rec[0] is Sequence:
		# We do not have a sequence here... create it and return it.
		self.__dict__[key] = Sequence(self, rec[1])
	        return self.__dict__[key]
	    else:
	        # Otherwise, return the default value
	        return copy.copy(rec[0])

    def __setattr__(self, key, value):
        '''Before we set a value, several things happen:
	1. If the relation is uni-directional, just set the value or, in case
	   of a Sequence, append the value to a list.
	2. In case of a bi-directional relationship:
	   a. First remove a possible already existing relationship (not that
	      both sides can have a ultiplicity of '1'.
	   b. Set up a new relationship between self-value and value-self.'''

	rec = self.__get_attr_info (key, self.__class__)
	if len(rec) == 2: # Attribute or one-way relation
	    self.__dict__[key] = value
	else:
	    xrec = value.__get_attr_info (rec[2], value.__class__)
	    if self.__dict__[key]:
	        xself = self.__dict__[key]
		# Keep the relationship if we have a n:m relationship
		if rec[0] is not Sequence or xrec[0] is not Sequence:
		    if rec[0] is Sequence:
			del self.__dict__[key].list[xself]
		    else:
		        del self.__dict__[key]
		    if xrec[0] is Sequence:
			del xself.__dict__[key].list[self]
		    else:
		        del xself.__dict__[key]
	    
    def __delattr__(self, name):

    def sequence_remove(self, seq, obj):
        '''Remove an entry. Should only be called by Sequence's implementation.
	This function is used to trap the 'del' function.'''
	def del_attr (self, key, value, rec):
	    if rec[0] is not Sequence:
		del self.__dict__[key]
	    else:
		if not self.__dict__.has_key(key):
		    self.__dict__[key] = Sequence(self, rec[1])
		self.__dict__[key]._remove(value)

        key = None
	# Find the name for the Sequence...
        for k in self.__dict__.keys():
	    if self.__dict__[k] is seq:
		key = k
		break
	if key is None:
	    return
	rec = self.__get_attr_info (key, self.__class__)
	if len(rec) == 2: # One-way relation
	    del_attr (self, key, obj, rec)
	else:
	    xrec = obj.__get_attr_info (rec[2], obj.__class__)
	    del_attr (self, key, obj, rec)
	    try:
		del_attr (obj, rec[2], self, xrec)
	    except AttributeError, e:
		self.__dict__[key]._add(obj)
		raise e

# END Element


if __name__ == '__main__':

    print "\n============== Starting Element tests... ============\n"

    print "=== 1 ==="

    class A(Element): _attrdef = { }

    A._attrdef["str"] = ( "one", types.StringType )
    A._attrdef["seq"] = ( Sequence, types.StringType )

    a = A(1)

    assert a.str == 'one'
    assert a.seq.list == [ ]

    aap = "aap"
    noot = "noot"
    a.str = aap
    assert a.str is aap

    a.seq = aap
    assert a.seq.list == [ aap ]

    a.seq = noot
    assert a.seq.list == [ aap, noot ]

    a.seq.remove(aap)
    assert a.seq.list == [ noot ]

    print "=== 1:1 ==="

    class A(Element): _attrdef = { }

    A._attrdef['ref1'] = ( None, A, 'ref2' )
    A._attrdef['ref2'] = ( None, A, 'ref1' )

    a = A(1)

    assert a.ref1 is None
    assert a.ref2 is None

    a.ref1 = a
    assert a.ref1 is a
    assert a.ref2 is a

    del a.ref1
    assert a.ref1 is None
    print a.ref2
####    assert a.ref2 is None

    a = A(1)
    b = A(2)
    
    a.ref1 = b
    assert a.ref1 is b
    assert a.ref2 is None
    assert b.ref1 is None
    assert b.ref2 is a

    a.ref1 = a
    assert a.ref1 is a
    assert a.ref2 is a
    assert b.ref1 is None
####    assert b.ref2 is None

    print "=== 1:n ==="

    class A(Element): _attrdef = { }

    A._attrdef['ref'] = ( None, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'ref' )

    a = A(1)

    assert a.ref is None
    assert a.seq.list == [ ]

    a.ref = a
    assert a.ref is a
    assert a.seq.list == [ a ]

    del a.seq[a]
    assert a.ref is None
    assert a.seq.list == [ ]

    a.seq = a
    assert a.ref is a
    assert a.seq.list == [ a ]

    a = A(1)
    b = A(2)

    a.ref = a
    assert a.ref is a
    assert a.seq.list == [ a ]
    assert b.ref is None
    assert b.seq.list == [ ]

    a.ref = b
    assert a.ref is b
    assert a.seq.list == [ ]
    assert b.ref is None
    assert b.seq.list == [ a ]

    b.ref = b
    assert a.ref is b
    assert a.seq.list == [ ]
    assert b.ref is b
    assert b.seq.list == [ a, b ]

    del b.seq[a]
    assert a.ref is None
    assert a.seq.list == [ ]
    assert b.ref is b
    assert b.seq.list == [ b ]

