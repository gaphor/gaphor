# vim: sw=4
''' Element.py -- Base class for all UML model objects

All model elements (including diagrams) are inherited from Element. Element
keeps track of relations between objects.
If a relationship is bi-directional, the element will add itself to the
specified object on the opposite end.

If an element attribute is a list of items (multiplicity `*') the Sequence
class is used to represent a list. You can simply add items to the sequence
by defining
	object.sequence_attribute = some_other_object
If you want to remove the reference use:
	del object.sequence_attribute[some_other_object]

All information the Element needs in retrieved from the Element._attrdef
structure. This is a dictionary with the possible attribute names as keys and
a tupple as value.  A tupple contains two or three fields:
1. The default value of the attribute (e.g. 'NoName') or a reference to the
   Sequence class in case of a 0..* relationship.
2. Type of object that way be added.
3. In case of bi-directional relationships the third argument is the name
   by which the object is known on the other side.
'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')

import types, copy
from enumeration import Enumeration_
from sequence import Sequence, SequenceError
#from misc import Signal
from gaphor.misc.signal import Signal as _Signal

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

class Element:
    '''Element is the base class for *all* UML MetaModel classes. The
attributes and relations are defined by a <class>._attrdef structure.
A class does not need to define any local variables itself: Element will
retrieve all information from the _attrdef structure.
You should call Element::unlink() to remove all relationships with the element.

An element can send signals. All normal signals have the name of the attribute
that's altered. There are two special (system) signals:
__unlink__ and __relink__. __unlink__ is emited if the object is 'destroyed',
__relink__ is used if the object is active again due to a undo action in
one of the diagrams.
The signals protocol is:
	For single relationships:
		(signal_name, value_before, value_after) 
	for sequences:
		(signal_name, 'add'/'remove', value_to_add_or_remove)
	for 'system' signals:
		(__signal_name__, None, None)
'''

    _attrdef = { 'documentation': ( "", types.StringType ) }

    def __init__(self, id):
	#print "New object of type", self.__class__
	self.__dict__['__id'] = id
	self.__dict__['__signal'] = _Signal()
	self.__dict__['__presentation'] = [ ]

    def __unlink(self):
	#if elements.has_key(self.__dict__['__id']):
	#    del elements[self.__dict__['__id']]
	#print 'Element.__unlink()', self
        self.__emit("__unlink__", None, None)
	for key in self.__dict__.keys():
	    # In case of a cyclic reference, we should check if the element
	    # not yet has been removed.
	    if self.__dict__.has_key (key) and not key.startswith('__'):
		#print 'deleting key:', key
		if isinstance (self.__dict__[key], Sequence):
		    # Remove each item in the sequence, then remove
		    # the sequence from __dict__.
		    list = self.__dict__[key].list
		    while len (list) > 0:
		        del self.__dict__[key][list[0]]
		    assert len (self.__dict__[key].list) == 0
		    del self.__dict__[key]
		else:
		    # do a 'del self.key'
		    self.__delattr__(key)
	# Note that empty objects may be created in the object due to lookups
	# from objects with connected signals.
    	#print self.__dict__
    
    def unlink(self):
	'''Remove all references to the object.'''
	#print 'Element.unlink():', self
	# Notify other objects that we want to unlink()
	self.__unlink ()
	if self.__dict__.has_key ('__undodata'):
	    del self.__dict__['__undodata']

    # Hooks for presentation elements to add themselves:
    def add_presentation (self, presentation):
	'''A presentation element is linked to the Element. If the element was
	first __unlink__'ed, it is __relink__'ed again.'''
	pres = self.__dict__['__presentation']
        if not presentation in pres:
	    pres.append (presentation)
	    if (len(pres) == 1) and \
	    		self.__dict__.has_key('__undodata'):
		self.__load_undo_data()
		self.__emit('__relink__', None, None)

    def remove_presentation (self, presentation):
	'''Remove a presentation element from the list. If no more presentation
	elements are active, the object s unlinked.'''
        #print 'remove_presentation', self, presentation
	pres = self.__dict__['__presentation']
        if presentation in pres:
	    pres.remove(presentation)
	    if len (pres) == 0:
		print self, 'No more presentations: unlinking...'
		self.__save_undo_data()
		# unlink, but do not destroy __undo_data
	        self.__unlink()
    
    def presentations (self):
        return self.__dict__['__presentation']

    def __load_undo_data (self):
        #print 'undo_presentation', self.__dict__
	assert self.__dict__.has_key ('__undodata')
	undodata = self.__dict__['__undodata']
	for key in undodata.keys ():
	    #print 'setting key:', key
	    value = undodata[key]
	    #print 'Undoing value', key
	    if isinstance (value, types.ListType):
		for item in value:
		    setattr (self, key, item)
	    else:
		setattr (self, key, value)
	del self.__dict__['__undodata']

    def __save_undo_data (self):
	if len (self.__dict__['__presentation']) == 0:
	    # Create __undodata, so we can undo the element's state
	    undodata = { }
	    for key in self.__dict__.keys():
		if not key.startswith('__'):
		    #print 'Preserving value for', key
		    value = self.__dict__[key]
		    if isinstance (value, Sequence):
			undodata[key] = copy.copy (value.list)
		    else:
			undodata[key] = value
	    self.__dict__['__undodata'] = undodata

    def __get_attr_info(self, key, klass):
        '''Find the record for 'key' in the <class>._attrdef map.'''
	done = [ ]
	def real_get_attr_info(key, klass):
	    if klass in done:
	        return None
	    done.append(klass)
	    dict = klass._attrdef
	    #print 'Checking ' + klass.__name__
	    if dict.has_key(key):
		return dict[key]
	    else:
		for base in klass.__bases__:
		    rec = real_get_attr_info(key, base)
		    if rec is not None:
			return rec
	rec = real_get_attr_info(key, klass)
	if rec is None:
	    raise AttributeError, 'Attribute ' + key + \
		      ' is not in class ' + self.__class__.__name__
	else:
	    return rec

    def __ensure_seq(self, key, type):
	if not self.__dict__.has_key(key):
	    self.__dict__[key] = Sequence(self, type)
	return self.__dict__[key]

    def get(self, key):
	if self.__dict__.has_key(key):
	    # Key is already in the object
	    return self.__dict__[key]
	else:
	    info = self.__get_attr_info (key, self.__class__)
	    if info[0] is Sequence:
		# We do not have a sequence here... create it and return it.
		self.__dict__[key] = Sequence(self, info[1])
		return self.__dict__[key]
	    else:
	        # Otherwise, return the default value
	        return copy.copy(info[0])

    def __set(self, key, obj):
	old_value = None
	if self.__dict__.has_key(key):
	    old_value = self.__dict__[key]
	self.__dict__[key] = obj
	self.__queue(key, old_value, obj)

    def __del(self, key, dummy=None):
	'''Remove an attribute.'''
	old_value = None
	if self.__dict__.has_key(key):
	    old_value = self.__dict__[key]
	    del self.__dict__[key]
	    self.__emit(key, old_value, None)

    def __sequence_add(self, key, obj):
	if not self.__dict__.has_key(key):
	    info = self.__get_attr_info(key, self.__class__)
	    self.__dict__[key] = Sequence(self, info[1])
	seq = self.__dict__[key]
	self.__real_sequence_add(key, seq, obj)

    def __real_sequence_add(self, key, seq, obj):
	list = seq.list
	if list.count(obj) == 0:
	    list.append(obj)
	    list.sort()
	    self.__queue(key, 'add', obj)

    def __sequence_remove(self, key, obj):
	self.__emit(key, 'remove', obj)
	self.__dict__[key].list.remove(obj)

    def __getattr__(self, key):
	if key == 'id':
	    return self.__dict__['__id']
	else:
	    return self.get(key)

    def __setattr__(self, key, value):
        '''Before we set a value, several things happen:
	1. If the relation is uni-directional, just set the value or, in case
	   of a Sequence, append the value to a list.
	2. In case of a bi-directional relationship:
	   a. First remove a possible already existing relationship (not that
	      both sides can have a multiplicity of '1'.
	   b. Set up a new relationship between self-value and value-self.'''

	info = self.__get_attr_info (key, self.__class__)
	#print 'Element:__setattr__(' + key + ')' + str(rec)
	if len(info) == 2: # Attribute or one-way relation
	    if info[0] is Sequence:
	        self.__sequence_add(key, value)
	    else:
		self.__set(key, value)
	else:
	    xkey = info[2]
	    xinfo = value.__get_attr_info (xkey, value.__class__)

	    #print '__setattr__x', xrec
	    if len(xinfo) > 2:
	        assert xinfo[2] == key

	    # We have to remove our reference from the current 'other side'
	    if self.__dict__.has_key(key) and info[0] is not Sequence:
	        xself = self.__dict__[key]
		if xinfo[0] is Sequence:
		    xself.__sequence_remove(xkey, self)
		else:
		    xself.__del(xkey)
		xself.__flush()

	    # Establish the relationship
	    if info[0] is Sequence:
	    	#print 'add to seq'
		self.__sequence_add(key, value)
	    else:
		#print 'add to item'
		self.__set(key, value)

	    if xinfo[0] is Sequence:
		#print 'add to xseq'
		value.__sequence_add(xkey, self)
	    else:
		#print 'add to xitem'
		value.__set(xkey, self)
	    value.__flush()
	self.__flush()

    def __delattr__(self, key):
	info = self.__get_attr_info (key, self.__class__)
	if info[0] is Sequence:
	    raise AttributeError, 'Element: you can not remove a sequence'
	if not self.__dict__.has_key(key):
	    return

	if len(info) > 2:
	    xself = self.__dict__[key]
	    xkey = info[2]
	    xinfo = xself.__get_attr_info (xkey, info[1])
	    if xinfo[0] is Sequence:
		xself.__sequence_remove(xkey, self)
	    else:
		xself.__del(xkey)
	    xself.__flush()
	self.__del(key)
	self.__flush()

    def sequence_add(self, seq, obj):
	'''Add an entry. Should only be called by Sequence instances.
	This function adds an object to the sequence.'''
	for key in self.__dict__.keys():
	    if self.__dict__[key] is seq:
	        break
	self.__real_sequence_add(key, seq, obj)
	self.__flush()

    def sequence_remove(self, seq, obj):
        '''Remove an entry. Should only be called by Sequence's implementation.
	This function is used to trap the 'del' function.'''
	# Find the key that belongs to 'seq'
	for key in self.__dict__.keys():
	    if self.__dict__[key] is seq:
	        break
	#print 'Element.sequence_remove', key
	#seq_len = len (seq)
	info = self.__get_attr_info (key, self.__class__)
	if info[0] is not Sequence:
	    raise AttributeError, 'Element: This should be called from Sequence'
	seq.list.remove(obj)
	if len(info) > 2:
	    xself = obj
	    xkey = info[2]
	    xinfo = xself.__get_attr_info (xkey, info[1])
	    if xinfo[0] is Sequence:
		xself.__sequence_remove(xkey, self)
	    else:
		xself.__del(xkey)
	self.__flush()

    # Functions used by the signal functions
    def connect (self, signal_func, *data):
	self.__dict__['__signal'].connect (signal_func, *data)

    def disconnect (self, signal_func):
	self.__dict__['__signal'].disconnect (signal_func)

    def __queue (self, key, old_value_or_action, new_value):
	self.__dict__['__signal'].queue (key, old_value_or_action, new_value)

    def __flush (self):
	self.__dict__['__signal'].flush ()

    def __emit (self, key, old_value_or_action, new_value):
	self.__dict__['__signal'].emit (key, old_value_or_action, new_value)

    def save(self, store):
	for key in self.__dict__.keys():
	    if not key.startswith('__'):
		obj = self.__dict__[key]
		if isinstance (obj, Sequence):
		    for item in obj.list:
			store.save_attribute (key, item)
		else:
		    store.save_attribute (key, obj)
	return None

    def load(self, store):
	for name, value in store.values().items():
	    attr_info = self.__get_attr_info (name, self.__class__)
	    if issubclass (attr_info[1], types.IntType) or \
	       issubclass (attr_info[1], types.LongType):
		self.__dict__[name] = int (value)
	    elif issubclass (attr_info[1], types.FloatType):
		self.__dict__[name] = float (value)
	    else:
		if value and value != '':
		    self.__dict__[name] = value
	    self.__queue (name, None, value)
	
	for name, reflist in store.references().items():
	    attr_info = self.__get_attr_info (name, self.__class__)
	    for refelem in reflist:
		if not isinstance (refelem, attr_info[1]):
		    raise ValueError, 'Referenced item is of the wrong type'
		if attr_info[0] is Sequence:
		    self.__ensure_seq (name, attr_info[1])
		    if refelem not in self.__dict__[name]:
			self.__dict__[name].list.append (refelem)
			self.__queue (name, 'add', refelem)
		else:
		    self.__dict__[name] = refelem
		    self.__queue (name, None, refelem)

    def postload (self, store):
	'''Do some things after the items are initialized... This is basically
	used for Diagrams.'''
	self.__flush()

###################################
# Testing
if __name__ == '__main__':

    print '\n============== Starting Element tests... ============\n'

    print '=== Sequence: ',

    class A(Element): _attrdef = { }

    A._attrdef['seq'] = ( Sequence, types.StringType )

    a = A(1)
    assert a.seq.list == [ ]

    aap = 'aap'
    noot = 'noot'
    mies = 'mies'

    a.seq = aap
    assert a.seq.list == [ aap ]

    a.seq = noot
    assert a.seq.list == [ aap, noot ]

    assert len(a.seq) == 2
    assert a.seq[0] is aap
    assert a.seq[1] is noot
    assert aap in a.seq
    assert noot in a.seq
    assert mies not in a.seq

    a.unlink()
    del a

    #assert len (elements) == 0

    print '\tOK ==='

    print '=== Single:',

    class A(Element): _attrdef = { }

    A._attrdef['str'] = ( 'one', types.StringType )
    A._attrdef['seq'] = ( Sequence, types.StringType )

    a = A(2)

    assert a.str == 'one'
    assert a.seq.list == [ ]

    aap = 'aap'
    noot = 'noot'
    a.str = aap
    assert a.str is aap

    a.seq = aap
    assert a.seq.list == [ aap ]

    a.seq = noot
    assert a.seq.list == [ aap, noot ]

    a.seq.remove(aap)
    assert a.seq.list == [ noot ]

    a.unlink()

    #assert len (elements) == 0

    print '\tOK ==='

    print '=== 1:1:',

    class A(Element): _attrdef = { }

    A._attrdef['ref1'] = ( None, A, 'ref2' )
    A._attrdef['ref2'] = ( None, A, 'ref1' )

    a = A(3)

    assert a.ref1 is None
    assert a.ref2 is None

    a.ref1 = a
    #print a.ref1
    #print a.ref2
    assert a.ref1 is a
    assert a.ref2 is a

    del a.ref1
    assert a.ref1 is None
    #print a.ref2
    assert a.ref2 is None

    a.unlink()

    a = A(4)
    b = A(5)
    
    a.ref1 = b
    assert a.ref1 is b
    assert a.ref2 is None
    assert b.ref1 is None
    assert b.ref2 is a

    a.ref1 = a
    assert a.ref1 is a
    assert a.ref2 is a
    assert b.ref1 is None
    assert b.ref2 is None

    a.unlink()
    b.unlink()

    #assert len (elements) == 0

    print '\tOK ==='

    print '=== 1:n',

    class A(Element): _attrdef = { }

    A._attrdef['ref'] = ( None, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'ref' )

    a = A(6)

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

    b = A(7)
    a.seq = b
    assert b.ref is a
    assert a.seq.list == [ a, b ]

    
    del a.seq[a]
    assert a.ref is None
    assert b.ref is a
    assert a.seq.list == [ b ]

    b.unlink()
    a.unlink()
    a = A(8)
    b = A(9)

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

    b.ref = b
    assert a.ref is b
    assert a.seq.list == [ ]
    assert b.ref is b
    assert b.seq.list == [ a, b ]

    del b.seq[a]
    assert a.ref is None, 'a.ref = ' + str(a.ref)
    assert a.seq.list == [ ]
    assert b.ref is b
    assert b.seq.list == [ b ]

    del b.ref
    assert a.ref is None
    assert a.seq.list == [ ]
    assert b.ref is None
    assert b.seq.list == [ ]

    a.unlink()
    b.unlink()

    #print elements
    #assert len (elements) == 0

    print '\tOK ==='

    print '=== n:m:',

    class A(Element): _attrdef = { }

    A._attrdef['seq1'] = ( Sequence, A, 'seq2' )
    A._attrdef['seq2'] = ( Sequence, A, 'seq1' )

    a = A(10)
    assert a.seq1.list == [ ]
    assert a.seq2.list == [ ]

    b = A(11)
    assert b.seq1.list == [ ]
    assert b.seq2.list == [ ]

    a.seq1 = a
    assert a.seq1.list == [ a ]
    assert a.seq2.list == [ a ]
    assert b.seq1.list == [ ]
    assert b.seq2.list == [ ]

    a.seq2 = a
    assert a.seq1.list == [ a ]
    assert a.seq2.list == [ a ]
    assert b.seq1.list == [ ]
    assert b.seq2.list == [ ]

    a.seq1 = b
    assert a.seq1.list == [ a, b ]
    assert a.seq2.list == [ a ]
    assert b.seq1.list == [ ]
    assert b.seq2.list == [ a ]

    del a.seq1[a]
    assert a.seq1.list == [ b ]
    assert a.seq2.list == [ ]
    assert b.seq1.list == [ ]
    assert b.seq2.list == [ a ]

    b.seq1 = a
    assert a.seq1.list == [ b ]
    assert a.seq2.list == [ b ]
    assert b.seq1.list == [ a ]
    assert b.seq2.list == [ a ]

    try:
	del a.seq1
    except AttributeError:
        pass
    except Exception:
        assert 0
    assert a.seq1.list == [ b ]
    assert a.seq2.list == [ b ]
    assert b.seq1.list == [ a ]
    assert b.seq2.list == [ a ]

    a.unlink()
    b.unlink()

    #assert len (elements) == 0

    print '\tOK ==='

    print '=== Signals:',

    class A(Element): _attrdef = { }

    A._attrdef['rel'] = ( Name, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'rel' )

    class Z:
	def callback (self, *data):
	    self.cb_data = data

    a = A(12)
    b = A(13)
    z = Z()
    y = Z()
    x = Z()
    a.connect (z.callback, 'one', 'two')
    #data = a.__dict__['__signals'][0]
    #assert data[0] == z.callback
    #assert data[1] == 'one'
    #assert data[2] == 'two'

    a.connect (y.callback, 'three')
    #data = a.__dict__['__signals'][0]
    #assert data[0] == z.callback
    #assert data[1] == 'one'
    #assert data[2] == 'two'
    #data = a.__dict__['__signals'][1]
    #assert data[0] == y.callback
    #assert data[1] == 'three'

    a.connect (x.callback)
    #data = a.__dict__['__signals'][2]
    #assert data[0] == x.callback
    
    a.rel = b
    assert z.cb_data[0] == 'rel'
    assert z.cb_data[1] == None  # old_value
    assert z.cb_data[2] == b     # new_value
    assert z.cb_data[3] == 'one'
    assert z.cb_data[4] == 'two'
    assert y.cb_data[0] == 'rel'
    assert y.cb_data[1] == None
    assert y.cb_data[2] == b
    assert y.cb_data[3] == 'three'
    
    a.disconnect (z.callback)
    #data = a.__dict__['__signals'][0]
    #assert len (a.__dict__['__signals']) == 2
    #assert data[0] == y.callback
    #assert data[1] == 'three'

    a.unlink()
    del a
    b.unlink()
    del b

    #assert len (elements) == 0

    print '\tOK ==='

    print '=== Unlink:',

    class A(Element): _attrdef = { }

    A._attrdef['rel'] = ( Name, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'rel' )

    a = A(17)
    b = A(18)

    #assert len (elements) == 2
    
    a.rel = b

    a.unlink()
    b.unlink()

    #assert len (elements) == 0

    print '\tOK ==='

    import gc

    gc.collect()
    assert gc.garbage == [ ]

    print '\n============== All Element tests passed... ==========\n'
