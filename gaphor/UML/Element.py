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
	if owner is not None:
	    self.owner = owner
	else:
	    self.owner = None
	self.requested_type = type
	self.list = []

    def __setitem__(self, key, value):
        self.modify(key, value)

    def __delitem__(self, key):
        self.remove(key)

    def add(self, obj):
	'''Append an entry to the Sequence. If the Sequence has an owner, the
	owners sequence_add() function is called (this is handy for
	bi-directional relationships).'''
	if self.owner:
	    self.owner.sequence_add(self, obj)
	else:
	    self._add(obj)

    def _add(self, obj):
	'''Append object 'obj' to the list. If 'obj' is already in the sequence
	nothing is done. This function should only be called by Element objects.
	'''
	if isinstance (obj, types.ListType):
	    for o in obj:
		self._add(o)
	else:
	    try:
		self.list.index(obj)
	    except ValueError: # 'obj' not found in 'list'
		if isinstance (obj, self.requested_type):
		    self.list.append(obj)
		else:
		    raise ValueError, "Sequence._add(obj): Object is not of type " + str(self.requested_type)

    def modify(self, old_obj, new_obj):
        self.remove(old_obj)
	self.add(new_obj)

    def remove(self, obj):
	'''Remove an entry from the Sequence.'''
	if self.owner:
	    self.owner.sequence_remove(self, obj)
	else:
	    self._remove(obj)

    def _remove(self, obj):
	'''This function is used to do the actual remove. This function should
	only be called by Element objects.'''
	try:
	    self.list.remove(obj)
	except ValueError:
	    raise ValueError, "Sequence._remove(obj): Object obj not in the sequence"


if __name__ == '__main__':
    def test(str):
       print str
       eval (str)

    print "\n============== Starting Sequence tests... ============\n"
    class A: pass
    class B(A): pass

    s = Sequence(None, types.StringType)

    print s._add.__doc__
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'
    test ('s._add (a)')
    test ('s._add (b)')
    print s.list

    test ('s._add (a)')
    print s.list

    test ('s._add([c, d])')
    print s.list
    
    try:
        test ('s._remove(\'e\')')
    except ValueError, e:
        print "Caught the exception:", e

    try:
    	test ('s._add(1)')
    except ValueError, e:
        print "Caught the exception:", e

    s = Sequence (None, A)
    a = A()
    b = B()
    test ('s._add (a)')
    test ('s._add (b)')
    print 'del s[a]'
    del s[a]
    print s.list

    print 's[b] = a'
    s[b] = a
    print s.list

    try:
    	test ('s._add(1)')
    except ValueError, e:
        print "Caught the exception:", e

# End of Sequence tests

#
# Base class for all UML model objects
#
# A word on the <class>__classdef__ structure:
# The <class>__classdef__ structures are dictionaries decribing the
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
#ModelElement__classdef__ = {
#   name	default value, default type, attribute name for opposite side
#    "name":	( "NoName", String )
#}

class Element:
    '''Element is the base class for *all* UML MetaModel classes. The
attributes and relations are defined by a <class>._attrdef structure.
A class does not need to define any local variables itself: Element will
retrieve all information from the _attrdef__ structure.'''
    _attrdef = { }
    def __init__(self, id):
	self.__dict__["_Element__id"] = id

    def __get_attr_info(self, key, klass):
        '''Find the record for 'key' in the <class>_attrdef__ map.'''
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
	def set_attr (self, key, value, rec):
	    if rec[0] is not Sequence or isinstance (value, Sequence):
		self.__dict__[key] = value
	    else:
	        if not self.__dict__.has_key(key):
		    self.__dict__[key] = Sequence(self, rec[1])
		self.__dict__[key]._add(value)

	rec = self.__get_attr_info (key, self.__class__)
	if len(rec) == 2: # Attribute or one-way relation
	    set_attr (self, key, value, rec)
	else:
	    xrec = value.__get_attr_info (rec[2], value.__class__)
	    # Here we do some magic: if one end of the association is not
	    # a sequence. If self.key is not a sequence, it will attempt
	    # to remove itself from value.rec[2]. If value.rec[2] is not a
	    # Sequence, it will attempt to disconnect itself from self.key.
	    # TODO: Write test cases that test 1:1, 1:n, n:1 and n:m
	    # relationships.
	    if rec[1] is not Sequence and self.__dict__.has_key(key) \
	        and self.__dict__[key].__dict__.has_key(rec[2]):
		# Remove value of self."key".rec[2]
		v = self.__dict__[key].__dict__[rec[2]]
		if isinstance(v, Sequence):
		    v.remove(self)
		else:
		    del v
	    if xrec[1] is not Sequence and value.__dict__.has_key(rec[2]) \
	        and value.__dict__[rec[2]].__dict__.has_key(key):
	        # Remove value from self."key"
		v = value.__dict__[rec[2]].__dict__[key]
		if isinstance(v, Sequence):
		    v.remove(value)
		else:
		    del v
	    set_attr (self, key, value, rec)
	    try:
		set_attr (value, rec[2], self, xrec)
	    except AttributeError, e:
	        self.__dict__[key]._remove(value)
		raise e

    def sequence_add(self, seq, obj):
        '''Add an entry. Should only be called by Sequence's implementation.'''
	key = None
	# Find the name for the Sequence...
        for k in self.__dict__.keys():
	    if self.__dict__[k] is seq:
		key = k
		break
	self.__setattr__(key, obj)

    def sequence_remove(self, seq, obj):
        '''Remove an entry. Should only be called by Sequence's implementation.'''
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
	    del_attr (self, key, value, rec)
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

    import gc

    print "\n============== Starting Element tests... ============\n"
    class A(Element): _attrdef = { }
    class B(Element): _attrdef = { }
    class C(B): _attrdef = { }

    A._attrdef["one"] = ( "one", types.StringType )
    A._attrdef["two"] = ( "two", types.StringType )
    A._attrdef["three"] = ( Sequence, types.StringType )
    A._attrdef["seq2seq"] = ( Sequence, B, "seq2seq" )
    A._attrdef["C"] = ( None, C )
    A._attrdef["ref2ref"] = ( None, B, "ref2ref" )
    A._attrdef["ref2seq"] = ( None, B, "seq2ref")

    B._attrdef["seq2seq"] = ( Sequence, A, "seq2seq" )
    B._attrdef["ref2ref"] = (None, A, "ref2ref")
    B._attrdef["seq2ref"] = ( Sequence, A, "ref2seq")

    C._attrdef["name"] = ( "NoName", String )

    a = A(1)
    b = B(2)
    c = C(3)
    d = C(4)

    print 'test Element class:'
    print 'id:', a.id

    try:
	print 'print a.thrww'
	print a.thrww
    except AttributeError, e:
        print "Error caught:", e

    print '\na.one = "wow" (simple attribute)'
    a.one = "wow"
    print a.one

    print 'a.three = "aap"'
    a.three = "aap"
    print a.three.list

    print 'a.three = "aap"'
    a.three = "aap"
    print a.three.list

    print 'a.three = "noot"'
    a.three = "noot"
    print a.three.list

    print '\nTesting sequences:'
    print 'a:', a.seq2seq.list
    print 'b:', b.seq2seq.list
    print 'c:', c.seq2seq.list

    print '\na.seq2seq = b'
    a.seq2seq = b
    print a.seq2seq.list
    print b.seq2seq.list
    print c.seq2seq.list

    print "\na.seq2seq = c"
    a.seq2seq = c
    print a.seq2seq.list
    print b.seq2seq.list
    print c.seq2seq.list

    print "\na.seq2seq.remove(b)"
    a.seq2seq.remove(b)
    print a.seq2seq.list
    print b.seq2seq.list
    print c.seq2seq.list

    print "\ndel a.seq2seq[d]"
    try:
	del a.seq2seq[d]
    except Exception, e:
        print "Exception caught:", e

    print a.seq2seq.list
    print b.seq2seq.list
    print c.seq2seq.list

    print "\ndel c.seq2seq[a]"
    del c.seq2seq[a]
    print a.seq2seq.list
    print b.seq2seq.list
    print c.seq2seq.list

    print "\na.ref2ref = b"
    a.ref2ref = b
    print a.ref2ref
    print b.ref2ref
    print c.ref2ref

    print "\na.ref2ref = c"
    a.ref2ref = c
    print a.ref2ref
    print b.ref2ref
    print c.ref2ref

    print "\nb.ref2ref = c"
    b.ref2ref = c
    print a.ref2ref
    print b.ref2ref
    print c.ref2ref

    print "\nb.seq2ref = a"
    b.seq2ref = a
    print a.ref2seq
    print b.seq2ref.list
    print c.seq2ref.list

    e = A(6)
    print "\nb.seq2ref = e"
    b.seq2ref = e
    print a.ref2seq
    print b.seq2ref.list
    print c.seq2ref.list
    print e.ref2seq

    print "\nc.seq2ref = a"
    c.seq2ref = a
    print a.ref2seq
    print b.seq2ref.list
    print c.seq2ref.list
    print e.ref2seq

    del ( a, b, c, d )
    gc.collect()
    print "unreachable:", gc.garbage

    f = A(11)
    g = B(12)
    h = C(13)

    f.seq2seq = g
    f.C = h

    #g.unlink()
    del g
    #h.unlink()
    del h

    print "\ndel f while g and h are already unref'ed"
    del f
    gc.collect()
    print "unreachable:", gc.garbage

# EOF
