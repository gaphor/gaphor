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

# A hash table contaiing all elements that are created. the key is the objects
# ID.
elements = { }

def lookup (id):
    try:
        return elements[id]
    except KeyError:
        return None

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
	    if self.list.count(obj) == 0:
		self.list.append(obj)
	else:
	    raise ValueError, 'Sequence._add(obj): Object is not of type ' + \
	    			str(self.requested_type)

    def remove(self, key):
        self.__delitem__(key)

    def index(self, key):
        return self.list.index(key)
    

class Element:
    '''Element is the base class for *all* UML MetaModel classes. The
attributes and relations are defined by a <class>._attrdef structure.
A class does not need to define any local variables itself: Element will
retrieve all information from the _attrdef structure.
You should call Element::unlink() to remove all relationships with the element.
In the unlink function all relationships are removed except presentation,
__id and __signals. Presentation items are removed by the diagram items that
represent them (they are connected to the 'unlink' signal). The element will
also be removed from the element_hash by unlink().

A special attribute is added: itemsOnUndoStack. This is a counter that is used
by the diagram item's implementation to avoid deletion (unlink()ing) of the 
object if references are lehd by the object on the undo stack.
'''
    _index = 1
    _attrdef = { 'presentation': ( Sequence, types.ObjectType ),
    		 'itemsOnUndoStack': (0, types.IntType ) }

    def __init__(self):
	#print "New object of type", self.__class__
	self.__dict__['__id'] = Element._index
	self.__dict__['__signals'] = [ ]
	elements[Element._index] = self
	Element._index += 1

    def unlink(self):
	'''Remove all references to the object. This will also remove the
	element from the `elements' table.'''
	#print 'Element.unlink():', self
	# Notify other objects that we want to unlink()
        self.emit("unlink")
	if elements.has_key(self.__dict__['__id']):
	    del elements[self.__dict__['__id']]
	for key in self.__dict__.keys():
	    # In case of a cyclic reference, we should check if the element
	    # not yet has been removed.
	    if self.__dict__.has_key (key) and \
			key not in ( 'presentation', 'itemsOnUndoStack', \
				     '__signals', '__id' ):
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
		    #print '\tunlink:', key
		    self.__delattr__(key)
	# Note that empty objects may be created in the object due to lookups
	# from objects with connected signals.
    	return self
    
    # Hooks for presentation elements to add themselves:
    def add_presentation (self, presentation):
        if not presentation in self.presentation:
	    self.presentation = presentation

    def remove_presentation (self, presentation):
        if presentation in self.presentation:
	    del self.presentation[presentation]
	    if len (self.presentation) == 0 and self.itemsOnUndoStack == 0:
		print self, 'No more presentations: unlinking...'
	        self.unlink()

    def undo_presentation (self, presentation):
        if not presentation in self.presentation:
	    # Add myself to the 'elements' hash 
	    if len (self.presentation) == 0:
	        elements[self.id] = self
	    self.presentation = presentation
	    self.itemsOnUndoStack -= 1
	    assert self.itemsOnUndoStack >= 0

    def remove_presentation_undoable (self, presentation):
        if presentation in self.presentation:
	    del self.presentation[presentation]
	    self.itemsOnUndoStack += 1
	    # Remove yourself from the 'elements' hash
	    if len (self.presentation) == 0:
	        if lookup (self.id):
		    del elements[self.id]

    def remove_undoability (self):
	if not self.__dict__.has_key ('itemsOnUndoStack'):
	    return
        self.itemsOnUndoStack -= 1
	assert self.itemsOnUndoStack >= 0
	if len (self.presentation) == 0 and self.itemsOnUndoStack == 0:
	    print self, ' No more presentations: unlinking...'
	    self.unlink()

    def __get_attr_info(self, key, klass):
        '''Find the record for 'key' in the <klass>._attrdef map.'''
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

    def __getattr__(self, key):
	if key == 'id':
	    return self.__dict__['__id']
	elif self.__dict__.has_key(key):
	    # Key is already in the object
	    return self.__dict__[key]
	else:
	    #if key[0] != '_':
		#print 'Unknown attr: Element.__getattr__(' + key + ')'
	    rec = self.__get_attr_info (key, self.__class__)
	    if rec[0] is Sequence:
		# We do not have a sequence here... create it and return it.
		return self.__ensure_seq (key, rec[1])
	    else:
	        # Otherwise, return the default value
	        return copy.copy(rec[0])

    def __setattr__(self, key, value):
        '''Before we set a value, several things happen:
	1. If the relation is uni-directional, just set the value or, in case
	   of a Sequence, append the value to a list.
	2. In case of a bi-directional relationship:
	   a. First remove a possible already existing relationship (not that
	      both sides can have a multiplicity of '1'.
	   b. Set up a new relationship between self-value and value-self.'''

	rec = self.__get_attr_info (key, self.__class__)
	#print 'Element:__setattr__(' + key + ')' + str(rec)
	if len(rec) == 2: # Attribute or one-way relation
	    if rec[0] is Sequence:
		#print '__setattr__', key, value
	        self.__ensure_seq (key, rec[1]).append(value)
	    else:
		self.__dict__[key] = value
	    self.emit (key)
	else:
	    xrec = value.__get_attr_info (rec[2], value.__class__)
	    #print '__setattr__x', xrec
	    if len(xrec) > 2:
	        assert xrec[2] == key
	    if self.__dict__.has_key(key):
		#print 'del old...'
	        xself = self.__dict__[key]
		# Keep the relationship if we have a n:m relationship
		if rec[0] is not Sequence or xrec[0] is not Sequence:
		    if rec[0] is Sequence:
			#print 'del-seq-item rec'
			#self.__del_seq_item(self.__dict__[key], xself)
			if xself in self.__dict__[key].list:
			    self.__dict__[key].list.remove(xself)
		    elif self.__dict__.has_key(key):
			    #print 'del-item rec'
			    del self.__dict__[key]
		    if xrec[0] is Sequence:
			#print 'del-seq-item xrec'
			#xself.__del_seq_item(xself.__dict__[rec[2]], self)
			xself.__dict__[rec[2]].list.remove (self)
		    elif xself.__dict__.has_key(rec[2]):
			    #print 'del-item xrec'
			    del xself.__dict__[rec[2]]
	    # Establish the relationship
	    if rec[0] is Sequence:
	    	#print 'add to seq'
		self.__ensure_seq(key, rec[1]).append (value)
	    else:
		#print 'add to item'
		self.__dict__[key] = value
	    if xrec[0] is Sequence:
		#print 'add to xseq'
		value.__ensure_seq(rec[2], xrec[1]).append (self)
	    else:
		#print 'add to xitem'
		value.__dict__[rec[2]] = self
	    self.emit (key)
	    value.emit (rec[2])
	    
    def __delattr__(self, key):
	rec = self.__get_attr_info (key, self.__class__)
	if rec[0] is Sequence:
	    raise AttributeError, 'Element: you can not remove a sequence'
	if not self.__dict__.has_key(key):
	    return
	xval = self.__dict__[key]
	if len(rec) > 2: # Bi-directional relationship
	    xrec = xval.__get_attr_info (rec[2], rec[1])
	    if xrec[0] is Sequence:
		#xval.__del_seq_item(xval.__dict__[rec[2]], self)
		#xval.__dict__[rec[2]].list.remove (self)
		# Handle it via sequence_remove()
		del xval.__dict__[rec[2]][self]
	    else:
	        del xval.__dict__[rec[2]]
		del self.__dict__[key]
		self.emit (key)
		xval.emit(rec[2])
	else:
	    del self.__dict__[key]
	    self.emit (key)

    def sequence_remove(self, seq, obj):
        '''Remove an entry. Should only be called by Sequence's implementation.
	This function is used to trap the 'del' function.'''
	# Find the key that belongs to 'seq'
	for key in self.__dict__.keys():
	    if self.__dict__[key] is seq:
	        break
	#print 'Element.sequence_remove', key
	#seq_len = len (seq)
	rec = self.__get_attr_info (key, self.__class__)
	if rec[0] is not Sequence:
	    raise AttributeError, 'Element: This should be called from Sequence'
	seq.list.remove(obj)
	if len(rec) > 2: # Bi-directional relationship
	    xrec = obj.__get_attr_info (rec[2], obj.__class__) #rec[1])
	    if xrec[0] is Sequence:
		obj.__dict__[rec[2]].list.remove (self)
	    else:
		del obj.__dict__[rec[2]]
	    obj.emit (rec[2])
	self.emit (key)
	#assert len (seq) == seq_len - 1

    # Functions used by the signal functions
    def connect (self, signal_func, *data):
	self.__dict__['__signals'].append ((signal_func,) + data)

    def disconnect (self, signal_func):
	self.__dict__['__signals'] = filter (lambda o: o[0] != signal_func,
					     self.__dict__['__signals'])

    def emit (self, key):
	#print 'emit', self, key
	#if not self.__dict__.has_key ('__signals'):
	#    print 'No __signals attribute in object', self
	#    return
        for signal in self.__dict__['__signals']:
	    signal_func = signal[0]
	    data = signal[1:]
	    #print 'signal:', signal_func, 'data:', data
	    signal_func (key, *data)

    def save(self, document, parent):
	def save_children (obj):
	    if isinstance (obj, Element):
		#subnode = document.createElement (key)
		subnode = document.createElement ('Reference')
		node.appendChild (subnode)
		subnode.setAttribute ('name', key)
		subnode.setAttribute ('refid', str(obj.__dict__['__id']))
	    elif isinstance (obj, types.IntType) or \
		    isinstance (obj, types.LongType) or \
	            isinstance (obj, types.FloatType):
		subnode = document.createElement ('Value')
		node.appendChild (subnode)
		subnode.setAttribute ('name', key)
		text = document.createTextNode (str(obj))
		subnode.appendChild (text)
	    elif isinstance (obj, types.StringType):
		subnode = document.createElement ('Value')
		node.appendChild (subnode)
		subnode.setAttribute ('name', key)
		cdata = document.createCDATASection (str(obj))
		subnode.appendChild (cdata)

        node = document.createElement (self.__class__.__name__)
	parent.appendChild (node)
	node.setAttribute ('id', str (self.__dict__['__id']))
	for key in self.__dict__.keys():
	    if key not in ( 'presentation', 'itemsOnUndoStack', \
	    		    '__signals', '__id' ):
		obj = self.__dict__[key]
		if isinstance (obj, Sequence):
		    for item in obj.list:
			save_children (item)
		else:
		    save_children (obj)
	return node

    def load(self, node):
	for child in node.childNodes:
	    if child.tagName == 'Reference':
		name = child.getAttribute ('name')
	        refid = int (child.getAttribute ('refid'))
		refelement = lookup (refid)
		attr_info = self.__get_attr_info (name, self.__class__)
		if not isinstance (refelement, attr_info[1]):
		    raise ValueError, 'Referenced item is of the wrong type'
		if attr_info[0] is Sequence:
		    self.__ensure_seq (name, attr_info[1])
		    if refelement not in self.__dict__[name]:
			self.__dict__[name].list.append (refelement)
			self.emit (name)
		else:
		    self.__dict__[name] = refelement
		    self.emit (name)
	    elif child.tagName == 'Value':
		name = child.getAttribute ('name')
		subchild = child.firstChild
		attr_info = self.__get_attr_info (name, self.__class__)
		if issubclass (attr_info[1], types.IntType) or \
		   issubclass (attr_info[1], types.LongType):
		    self.__dict__[name] = int (subchild.data)
		elif issubclass (attr_info[1], types.FloatType):
		    self.__dict__[name] = float (subchild.data)
		else:
		    self.__dict__[name] = subchild.data
		self.emit (name)

    def postload (self, node):
	'''Do some things after the items are initialized... This is basically
	used for Diagrams.'''
        pass

###################################
# Testing
if __name__ == '__main__':

    print '\n============== Starting Element tests... ============\n'

    print '=== Sequence: ',

    class A(Element): _attrdef = { }

    A._attrdef['seq'] = ( Sequence, types.StringType )

    a = A()
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

    assert len (elements) == 0

    print '\tOK ==='

    print '=== Single:',

    class A(Element): _attrdef = { }

    A._attrdef['str'] = ( 'one', types.StringType )
    A._attrdef['seq'] = ( Sequence, types.StringType )

    a = A()

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

    assert len (elements) == 0

    print '\tOK ==='

    print '=== 1:1:',

    class A(Element): _attrdef = { }

    A._attrdef['ref1'] = ( None, A, 'ref2' )
    A._attrdef['ref2'] = ( None, A, 'ref1' )

    a = A()

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

    a = A()
    b = A()
    
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

    assert len (elements) == 0

    print '\tOK ==='

    print '=== 1:n',

    class A(Element): _attrdef = { }

    A._attrdef['ref'] = ( None, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'ref' )

    a = A()

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

    b = A()
    a.seq = b
    assert b.ref is a
    assert a.seq.list == [ a, b ]

    
    del a.seq[a]
    assert a.ref is None
    assert b.ref is a
    assert a.seq.list == [ b ]

    b.unlink()
    a.unlink()
    a = A()
    b = A()

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
    assert a.ref is None
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
    assert len (elements) == 0

    print '\tOK ==='

    print '=== n:m:',

    class A(Element): _attrdef = { }

    A._attrdef['seq1'] = ( Sequence, A, 'seq2' )
    A._attrdef['seq2'] = ( Sequence, A, 'seq1' )

    a = A()
    assert a.seq1.list == [ ]
    assert a.seq2.list == [ ]

    b = A()
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

    assert len (elements) == 0

    print '\tOK ==='

    print '=== Signals:',

    class A(Element): _attrdef = { }

    A._attrdef['rel'] = ( Name, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'rel' )

    class Z:
	def callback (self, *data):
	    self.cb_data = data

    a = A()
    b = A()
    z = Z()
    y = Z()
    x = Z()
    a.connect (z.callback, 'one', 'two')
    data = a.__dict__['__signals'][0]
    assert data[0] == z.callback
    assert data[1] == 'one'
    assert data[2] == 'two'

    a.connect (y.callback, 'three')
    data = a.__dict__['__signals'][0]
    assert data[0] == z.callback
    assert data[1] == 'one'
    assert data[2] == 'two'
    data = a.__dict__['__signals'][1]
    assert data[0] == y.callback
    assert data[1] == 'three'

    a.connect (x.callback)
    data = a.__dict__['__signals'][2]
    assert data[0] == x.callback
    
    a.rel = b
    assert z.cb_data[0] == 'rel'
    assert z.cb_data[1] == 'one'
    assert z.cb_data[2] == 'two'
    assert y.cb_data[0] == 'rel'
    assert y.cb_data[1] == 'three'
    
    a.disconnect (z.callback)
    data = a.__dict__['__signals'][0]
    assert len (a.__dict__['__signals']) == 2
    assert data[0] == y.callback
    assert data[1] == 'three'

    a.unlink()
    del a
    b.unlink()
    del b

    assert len (elements) == 0

    print '\tOK ==='

    print '=== Unlink:',

    class A(Element): _attrdef = { }

    A._attrdef['rel'] = ( Name, A, 'seq' )
    A._attrdef['seq'] = ( Sequence, A, 'rel' )

    a = A()
    b = A()

    assert len (elements) == 2
    
    a.rel = b

    a.unlink()
    b.unlink()

    assert len (elements) == 0

    print '\tOK ==='

    import gc

    gc.collect()
    assert gc.garbage == [ ]

    print '\n============== All Element tests passed... ==========\n'
