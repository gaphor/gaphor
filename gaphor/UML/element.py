# vim: sw=4
""" Element.py -- Base class for all UML model objects

All model elements (including diagrams) are inherited from Element. Element
keeps track of relations between objects.
If a relationship is bi-directional, the element will add itself to the
specified object on the opposite end.

If an element attribute is a list of items (multiplicity '*') the Sequence
class is used to represent a list. You can simply add items to the sequence
by defining:
	object.sequence_attribute = some_other_object
If you want to remove the reference use:
	del object.sequence_attribute[some_other_object]

All information the Element needs in retrieved from the Element.__attributes__
structure. This is a dictionary with the possible attribute names as keys and
a tupple as value.  A tupple contains two or three fields:
1. The default value of the attribute (e.g. 'NoName') or a reference to the
   Sequence class in case of a 0..* relationship.
2. Type of object that way be added.
3. In case of bi-directional relationships the third argument is the name
   by which the object is known on the other side.
"""

import types, copy
from enum import Enum
from sequence import Sequence
from gaphor.misc.signal import Signal as _Signal

class AbstractClassError(Exception):
    pass

# Custom classes:
Multiplicity = str

class Element(object):
    """Element is the base class for *all* UML MetaModel classes.
    The attributes and relations are defined by a <class>.__attributes__
    structure.  A class does not need to define any local variables itself:
    Element will retrieve all information from the __attributes__ structure.

    You should call Element::unlink() to remove all relationships with the
    element.

    An element can send signals. All normal signals have the name of the
    attribute that's altered. There are two special (system) signals:
    __unlink__ and __relink__. __unlink__ is emited if the object is
    'destroyed', __relink__ is used if the object is active again due to
    an undo action in one of the diagrams (a presentation element is added
    to a previously unlinked element).

    The signals protocol is:
	    For single relationships:
		    (signal_name, value_before, value_after) 
	for sequences:
		(signal_name, 'add'/'remove', value_to_add_or_remove)
	for 'system' signals:
		(__signal_name__, None, None)
    """
    __abstract__ = True

    def __new__(klass, *args, **kwargs):
	if klass.__abstract__:
	    raise AbstractClassError, 'class %s is an abstract class' % klass.__name__
	return object.__new__(klass, *args, **kwargs)
    
    def __init__(self, id):
	#print "New object of type", self.__class__
	self.__dict__['__id'] = id
	self.__dict__['__signal'] = _Signal()
	self.__dict__['__presentation'] = list()

    # Public methods:

    def connect(self, signal_func, *data):
	"""Connect signal_func so it can recieve change notifications"""
	self.__dict__['__signal'].connect(signal_func, *data)

    def disconnect(self, signal_func):
	self.__dict__['__signal'].disconnect(signal_func)

    def add_presentation(self, presentation):
	"""A presentation element is linked to the Element.
	If the element was first __unlink__'ed, it is __relink__'ed again."""
	pres = self.__dict__['__presentation']
        if not presentation in pres:
	    pres.append(presentation)
	    if (len(pres) == 1) and \
	    		self.__dict__.has_key('__undodata'):
		self.__load_undo_data()
		self.__emit('__relink__', None, None)

    def remove_presentation(self, presentation):
	"""Remove a presentation element from the list.
	If no more presentation elements are active, the object s unlinked."""
        #print 'remove_presentation', self, presentation
	pres = self.__dict__['__presentation']
        if presentation in pres:
	    pres.remove(presentation)
	    if len(pres) == 0:
		print self, 'No more presentations: unlinking...'
		self.__save_undo_data()
		# unlink, but do not destroy __undo_data
	        self.__unlink()
    
    def presentations(self):
	"""Return a list of presentation elements that hold a reference to the
	element."""
        return self.__dict__['__presentation']

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self,c):
        """Returns true if the object is an instance of c"""
        return isinstance(self,c)

    def isTypeOf(self,anotherO):
        """Returns true if the object is of the same type as anotherO"""
        return type(self)==type(anotherO)

    # Lifecycle:

    def unlink(self):
	"""Remove all references to the object."""
	#print 'Element.unlink():', self
	# Notify other objects that we want to unlink()
	self.__unlink()
	if self.__dict__.has_key('__undodata'):
	    del self.__dict__['__undodata']

    # Saving and loading the element:

    def save(self, save_func):
	for key in self.__dict__.keys():
	    if not key.startswith('__'):
		obj = self.__dict__[key]
		if isinstance(obj, Sequence):
		    for item in obj.items:
			save_func(key, item)
			#store.save_attribute(key, item)
		else:
		    save_func(key, obj)
		    #store.save_attribute(key, obj)
	return None

    def load(self, name, value):
	#print self, name, value
	attr_info = self.__get_attribute(name)
	if attr_info[0] is Sequence:
	    self.__sequence_add(name, value)
	    #self.__ensure_seq(name, attr_info[1])
	    #if value not in self.__dict__[name]:
	    #    self.__dict__[name].items.append(value)
	    #    self.__queue(name, 'add', value)
	else:
	    if issubclass(attr_info[1], types.IntType) or \
	       issubclass(attr_info[1], types.LongType):
		self.__dict__[name] = int(value)
	    elif issubclass(attr_info[1], types.FloatType):
		self.__dict__[name] = float(value)
	    else:
		if value and value != '':
		    #print 'loading val:', value, 'for', name, self
		    self.__dict__[name] = value
	    self.__queue(name, None, value)
	
    def postload(self):
	"""Do some things after the items are initialized... This is basically
	used for Diagrams."""
	self.__flush()


    # Custom attribute access:

    def __getattr__(self, key):
	if key == 'id':
	    return self.__dict__['__id']
	else:
	    info = self.__get_attribute(key)
	    if info[0] is Sequence:
		# We do not have a sequence here... create it and return it.
		seq = self.__dict__[key] = Sequence(self, info[1])
		return seq
	    else:
	        # Otherwise, return the default value
	        return copy.copy(info[0])

    def __setattr__(self, key, value):
        """Before we set a value, several things happen:
	1. If the relation is uni-directional, just set the value or, in case
	   of a Sequence, append the value to a list.
	2. In case of a bi-directional relationship:
	   a. First remove a possible already existing relationship (not that
	      both sides can have a multiplicity of '1'.
	   b. Set up a new relationship between self-value and value-self."""

	info = self.__get_attribute(key)
	#print 'Element:__setattr__(' + key + ')' + str(rec)
	if len(info) == 2: # Attribute or one-way relation
	    if info[0] is Sequence:
	        self.__sequence_add(key, value)
	    else:
		self.__set(key, value)
	else:
	    # Handle a bi-directional relationship
	    xkey = info[2]
	    xinfo = value.__get_attribute(xkey)

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
	info = self.__get_attribute(key)
	if info[0] is Sequence:
	    raise AttributeError, 'Element: you can not remove a sequence'
	if not self.__dict__.has_key(key):
	    return

	if len(info) > 2:
	    xself = self.__dict__[key]
	    xkey = info[2]
	    xinfo = xself.__get_attribute(xkey)
	    if xinfo[0] is Sequence:
		xself.__sequence_remove(xkey, self)
	    else:
		xself.__del(xkey)
	    xself.__flush()
	self.__del(key)
	self.__flush()

    def __hash__(self):
	return hash(self.__dict__['__id'])

    # Private methods:

    def __unlink(self):
        self.__emit("__unlink__", None, None)
	for key in self.__dict__.keys():
	    # In case of a cyclic reference, we should check if the element
	    # not yet has been removed.
	    if self.__dict__.has_key(key) and not key.startswith('__'):
		#print 'deleting key:', key
		if isinstance(self.__dict__[key], Sequence):
		    # Remove each item in the sequence, then remove
		    # the sequence from __dict__.
		    items = self.__dict__[key].items
		    while len(items) > 0:
		        del self.__dict__[key][items[0]]
		    assert len(self.__dict__[key].items) == 0
		    del self.__dict__[key]
		else:
		    # do a 'del self.key'
		    self.__delattr__(key)
	# Note that empty objects may be created in the object due to lookups
	# from objects with connected signals.
    	#print self.__dict__
    
    def __load_undo_data(self):
        #print 'undo_presentation', self.__dict__
	assert self.__dict__.has_key('__undodata')
	undodata = self.__dict__['__undodata']
	for key in undodata.keys():
	    #print 'setting key:', key
	    value = undodata[key]
	    #print 'Undoing value', key
	    if isinstance(value, types.ListType):
		for item in value:
		    setattr(self, key, item)
	    else:
		setattr(self, key, value)
	del self.__dict__['__undodata']

    def __save_undo_data(self):
	if len(self.__dict__['__presentation']) == 0:
	    # Create __undodata, so we can undo the element's state
	    undodata = { }
	    for key in self.__dict__.keys():
		if not key.startswith('__'):
		    #print 'Preserving value for', key
		    value = self.__dict__[key]
		    if isinstance(value, Sequence):
			undodata[key] = copy.copy(value.items)
		    else:
			undodata[key] = value
	    self.__dict__['__undodata'] = undodata

    def __get_attribute(self, key):
        """Find the record for 'key' in the <class>.__attributes__ map."""
	try:
	    return self.__class__.__attributes__[key]
	except KeyError, e:
	    raise AttributeError, 'Attribute ' + key + \
		      ' is not in class ' + self.__class__.__name__

    def __set(self, key, obj):
	"Set a non-sequence attribute."
	old_value = None
	if self.__dict__.has_key(key):
	    # quit if the object is already set:
	    if self.__dict__[key] is obj:
		return
	    old_value = self.__dict__[key]
	self.__dict__[key] = obj
	self.__queue(key, old_value, obj)

    def __del(self, key, dummy=None):
	"""Remove a non-sequence attribute."""
	old_value = None
	if self.__dict__.has_key(key):
	    old_value = self.__dict__[key]
	    del self.__dict__[key]
	    self.__emit(key, old_value, None)

    # Handling sequences: all logic for adding/removing objects from
    # Sequences is in Element, not in Sequence!
    # The sequence calls Element.sequence_add()/sequence_remove() whenever
    # objects are added or removed from the sequence.

    def sequence_add(self, seq, obj):
	"""Add an entry. Should only be called by Sequence instances.
	This function adds an object to the sequence.
	This method is almost similar to __sequence_add, but does not check
	for existence of the sequence (since it is called from the sequence)"""
	# Find the key that belongs to 'seq'
	for key in self.__dict__.keys():
	    if self.__dict__[key] is seq:
	        break
	self.__real_sequence_add(key, seq, obj)
	self.__flush()

    def sequence_remove(self, seq, obj):
        """Remove an entry. Should only be called by Sequence's implementation.
	This function is used to trap the 'del' function."""
	# Find the key that belongs to 'seq'
	for key in self.__dict__.keys():
	    if self.__dict__[key] is seq:
	        break
	#print 'Element.sequence_remove', key
	#seq_len = len(seq)
	info = self.__get_attribute(key)
	if info[0] is not Sequence:
	    raise AttributeError, 'Element: This should be called from Sequence'
	#seq.items.remove(obj)
	self.__sequence_remove(key, obj)
	if len(info) > 2:
	    xkey = info[2]
	    xinfo = obj.__get_attribute(xkey)
	    if xinfo[0] is Sequence:
		obj.__sequence_remove(xkey, self)
	    else:
		obj.__del(xkey)
	self.__flush()

#    def __ensure_seq(self, key, type):
#	if not self.__dict__.has_key(key):
#	    self.__dict__[key] = Sequence(self, type)
#	return self.__dict__[key]

    def __sequence_add(self, key, obj):
	"""Like sequence_add, but a new sequence is create if ot does not
	already exists. This method is called from within Element."""
	if not self.__dict__.has_key(key):
	    info = self.__get_attribute(key)
	    seq = self.__dict__[key] = Sequence(self, info[1])
	    self.__real_sequence_add(key, seq, obj)
	elif obj not in self.__dict__[key]:
	    seq = self.__dict__[key]
	    self.__real_sequence_add(key, seq, obj)

    def __real_sequence_add(self, key, seq, obj):
	"""Add an object to a sequence, if the object is already in
	the sequence, nothing is done."""
	items = seq.items
	if items.count(obj) == 0:
	    items.append(obj)
	    items.sort(lambda a, b: a.id > b.id and 1 or -1)
	    self.__queue(key, 'add', obj)

    def __sequence_remove(self, key, obj):
	"Remove obj from the sequence known by key."
	self.__emit(key, 'remove', obj)
	self.__dict__[key].items.remove(obj)

    # Methods used for signals

    def __queue(self, key, old_value_or_action, new_value):
	self.__dict__['__signal'].queue(key, old_value_or_action, new_value)

    def __flush(self):
	self.__dict__['__signal'].flush()

    def __emit(self, key, old_value_or_action, new_value):
	self.__dict__['__signal'].emit(key, old_value_or_action, new_value)

