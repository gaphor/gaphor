#!/usr/bin/env python
# vim: sw=4
# MetaModel Parser: Parse the UML metamodel definition version 1.3 file
# as defined by the OMG and create python code to be used by Gaphor.
#
# Note that the output is written to STDOUT and the status messages and errors
# are written to STDERR.
#
# - Although References are stored, nothing is done with them, since they
#   we also have AssociationEnds, which contain the same information and more.
# - Note that this model is just a start. In the end the data model should be
#   narrowed to the model defined in chapter 5 of the OMG UML 1.4 specs
#   (Model Interchange Using XMI).
# - Once Gaphor is mature enough, the data model will be drawn in Gaphor
#   (for documentation and demonstration purposes) and Gaphor will provide
#   its own data model.
#
import sys, getopt
from xmllib import *
import types
import traceback

msg = sys.stderr.write

# Used to map DataTypes to Python primitives:
primitives = {
    'Geometry': 'list',
    'LocationReference': 'str',
    'Boolean': 'int',
    'String':'str',
    'UnlimitedInteger': 'long',
    'Integer': 'int',
    'Name': 'str'
}

# For those classes no class definition is generated:
custom_elements = [
    'Element',
    'PresentationElement', # ModelElement.presentation is set to not navigable
    'Multiplicity',
    'MultiplicityRange'
]

default_values = {
    'isNavigable': 'True',
    'Name': '\'\'',
    'Boolean': 'False',
    'VisibilityKind': 'VK_PUBLIC',
    'OrderingKind': 'OK_UNORDERED',
    'ChangeableKind': 'CK_CHANGEABLE',
    'ScopeKind': 'SK_INSTANCE',
    'PseudostateKind': 'PK_CHOICE',
    'ParameterDirectionKind': 'PDK_IN',
    'AggregationKind': 'AK_NONE',
    'CallConcurrencyKind': 'CCK_SEQUENTIAL',
    'Expression': 'None',
    'ActionExpression': 'None',
    'IterationExpression': 'None',
    'MappingExpression': 'None',
    'BooleanExpression': 'None',
    'TimeExpression': 'None',
    'TypeExpression': 'None',
    'ObjectSetExpression': 'None',
    'ProcedureExpression': 'None',
    'ArgListsExpression': 'None',
    'Multiplicity': '\'\'', # Defaults to String
    'Integer': '1', # Defaults to Int
    'UnlimitedInteger': '1', # Defaults to Long
    'String': '\'\'', # Defaults to String
    'Geometry': 'None', # Defaults to a list (of length 4)
    'LocationReference': 'None'
}

translations = {
    'ActivityGraph.partition': (lambda a: a, 'isNavigable', False),
    'Classifier.collaboration': (lambda a: a, 'name', 'classifierCollaboration'),
    'Classifier.classifierRole': (lambda a: a, 'name', 'classifierBaseRole'),
    'Collaboration.collaboration': (lambda a: a, 'isNavigable', False),
    'Collaboration.participatingLink': (lambda a: a, 'isNavigable', False),
    'CollaborationInstanceSet.collaboration': (lambda a: a, 'isNavigable', False),
    'Feature.classifierRole': (lambda a: a.other_end(), 'isNavigable', False),
    'Instance.collaborationInstanceSet': (lambda a: a, 'isNavigable', False),
    'Link.owner': (lambda a: a, 'name', 'linkOwner'),
    'Link.playedRole': (lambda a: a, 'name', 'playedAssociationRole'),
    'Link.collaborationInstanceSet': (lambda a: a, 'isNavigable', False),
    'Message.sender': (lambda a: a.other_end(), 'isNavigable', False),
    'Message.receiver': (lambda a: a.other_end(), 'isNavigable', False),
    'ModelElement.collaborationInstanceSet': (lambda a: a, 'isNavigable', False),
    'ModelElement.presentation': (lambda a: a, 'isNavigable', False),
    'Operation.collaboration': (lambda a: a, 'name', 'operationCollaboration'),
    'Package.elementImport': (lambda a: a, 'name', 'packageImport'),
    'State.entry': (lambda a: a.other_end(), 'name', 'entryState'),
    'State.exit': (lambda a: a.other_end(), 'name', 'exitState'),
    'State.doActivity': (lambda a: a.other_end(), 'name', 'doActivityState'),
    'Stimulus.argument': (lambda a: a.other_end(), 'name', 'argumentStimulus'),
    'Stimulus.sender': (lambda a: a.other_end(), 'name', 'senderStimulus'),
    'Stimulus.receiver': (lambda a: a.other_end(), 'name', 'receiverStimulus'),
}

# An overall dictionary where all elements will be indexed by their id
elements = { }

# Data classes

class ModelElement:
    def __init__(self, id, name):
	global elements
	self.id = id
	self.name = name
	elements[id] = self
    
    def resolve_references(self):
	pass

class Package(ModelElement):
    def __init__(self, id, name):
	ModelElement.__init__(self, id, name)
	self.imports = [ ]
	self.datatypes = [ ]
	self.classes = [ ]
	self.associations = [ ]
	
    def add_import(self, i):
	self.imports.append(i)
	
    def add_datatype(self, d):
	self.datatypes.append(d)
	
    def add_class(self, c):
	self.classes.append(c)
	
    def add_association(self, a):
	self.associations.append(a)

class Import(ModelElement):
    def __init__(self, id, name, importedNamespace):
	ModelElement.__init__(self, id, name)
	self.importedNamespace = importedNamespace

    def resolve_references(self):
	global elements
	self.importedNamespace = elements[self.importedNamespace]

    def str(self):
	return 'from %s import *\n' % self.importedNamespace.name

class Class(ModelElement):
    def __init__(self, id, name, isAbstract, supertypes):
	ModelElement.__init__(self, id, name)
	self.isAbstract = isAbstract == 'true'
	self.supertypes = supertypes and supertypes.split(' ') or None
	self.attributes = [ ]
	self.references = [ ]
	self.associationEnds = [ ]

    def add_attribute(self, a):
	self.attributes.append(a)

    def add_reference(self, r):
	self.references.append(r)

    def add_association_end(self, ae):
	self.associationEnds.append(ae)

    def is_referenced(self, ae):
	for r in self.references:
	    if r.referencedEnd is ae:
		return True
	return False

    def resolve_references(self):
	global elements
	if self.supertypes:
	    n = [ ]
	    for id in self.supertypes:
		n.append(elements[id])
	    self.supertypes = n
	
    def doimpl(self, done):
	"Create a string containing all attributes and associations."
	if self in done:
	    return ''
	s = ''
	for t in self.supertypes or ():
	    s += t.doimpl(done)
	if self.attributes or self.references:
	    s += '    # from %s:\n' % self.name
	# Build attributes: 'name': (default value, type)
	for a in self.attributes:
	    s += '    ' + a.str() + ',\n'
	# Build associations: 'name': (default or 'Sequence', type[, other_end])
	#for r in self.references:
	#    s += '    ' + r.str() + ',\n'
	for e in self.associationEnds:
	    if e.str() != '':
		s += '    ' + e.str() + ',\n'
	done.append(self)
	return s

    def defstr(self, done):
	"""Return the class definition. the list done is used to create
	definitions of supertypes before the actual class."""
	if self in done:
	    return ''
	s = ''
	for t in self.supertypes or ():
	    s += t.defstr(done)
	s += 'class %s(' % self.name
	if self.supertypes:
	    for t in self.supertypes:
		s += '%s,' % t.name
	else:
	    s += 'Element,'
	s = s[:-1] + '): __abstract__ = %s\n' % (self.isAbstract and 'True' or 'False')
	done.append(self)
	return s

    def implstr(self):
	"Return the dict structure here"
	if self.isAbstract:
	    return ''
	s = '%s.__attributes__ = {\n' % self.name
	s += self.doimpl([ ])
	s = s[:-2] + '\n}\n\n'
	return s

class DataType(ModelElement):
    def __init__(self, id, name):
	ModelElement.__init__(self, id, name)
	self.isEnumeration = 0
	self.enumvalues = [ ]

    def is_enumeration(self):
	self.isEnumeration = 1

    def add_enumvalue(self, val):
	self.enumvalues.append(val)

    def str(self):
	s = ''
	if self.isEnumeration:
	    for e in self.enumvalues:
		s = s + "%s = '%s'\n" % (e.upper(), e)
	    s += 'class %s(Enum):\n' % self.name
	    s += '    _values = ['
	    for e in self.enumvalues:
		s += ' %s,' % e.upper()
	    s = s[:-1] + ' ]\n\n'
	else:
	    s = 'class %s(%s): pass\n\n' % (self.name, primitives[self.name])
	return s

class Attribute(ModelElement):
    def __init__(self, id, name, type):
	ModelElement.__init__(self, id, name)
	self.type = type
	self.multiplicity = None

    def set_multiplicity(self, m):
	self.multiplicity = m

    def resolve_references(self):
	global elements
	self.type = elements[self.type]

    def str(self):
	s = "'%s': ( " % self.name
	if default_values.has_key(self.name):
	    s += '%s' % default_values[self.name]
	else:
	    try:
		s += '%s' % default_values[self.type.name]
	    except KeyError, e:
		msg('No default value found for type %s' % self.type.name)
		s += 'None'
	s += ', %s )' % self.type.name
	return s

class Reference(Attribute):
    def __init__(self, id, name, type, referencedEnd):
	Attribute.__init__(self, id, name, type)
	self.referencedEnd = referencedEnd

    def resolve_references(self):
	Attribute.resolve_references(self)
	global elements
	self.referencedEnd = elements[self.referencedEnd]
	# Set it navigable:
	#self.referencedEnd.isNavigable = True

    def str(self):
	return self.referencedEnd.str()[:-4]

class Association(ModelElement):
    def __init__(self, id, name):
	ModelElement.__init__(self, id, name)
	self.associationEnds = [ ]

    def add_association_end(self, ae):
	self.associationEnds.append(ae)

    def other_end(self, ae):
	if ae is self.associationEnds[0]:
	    return self.associationEnds[1]
	else:
	    return self.associationEnds[0]

class AssociationEnd(ModelElement):
    def __init__(self, id, name, type, association, isNavigable):
	ModelElement.__init__(self, id, name)
	self.type = type
	self.isNavigable = isNavigable == 'true'
	self.multiplicity = None #Multiplicity(1, 1, 'false', 'false')
	self.association = association

    def set_multiplicity(self, m):
	self.multiplicity = m

    def resolve_references(self):
	global elements
	self.type = elements[self.type]

    def other_end(self):
	return self.association.other_end(self)

    def str(self):
	if not self.isNavigable:
	    return ''

	s = "'%s': ( %s, %s" % (self.name, self.multiplicity.str(), self.type.name)
	# Get the association end on the other end of the association:
	e = self.other_end()
	# Add reverse entry if the other end is navigable too:
	if e.isNavigable:
	    s += ", '%s'" % e.name
	s += ' )'
	return s

class Multiplicity:
    def __init__(self, lower, upper, isOrdered, isUnique):
	self.lower = lower
	self.upper = upper
	self.isOrdered = isOrdered == 'true'
	self.isUnique = isUnique == 'true'

    def str(self):
	if self.upper == -1:
	    return 'Sequence'
	return 'None'

# UML 1.3 namespace (don't forget the trailing space):
NS='omg.org/mof.Model/1.3 '

# This is the parser. It's a bit hackish and maybe it only works for the
# UML 1.3 MetaModel (which is enough actually). The parser is stack based:
# for packages, classes, datatypes and associations new maps are created.
class MetaModelParser(XMLParser):

    def __init__(self, **kw):
	self.mmstack = [ ]
	self.xmifield = None
	# These are the elements we can expect in the MetaModel:
	self.elements = {
	    'XMI': (self.start_XMI, self.end_XMI),
	    'XMI.CorbaTcAlias': (self.start_XMI, self.end_XMI),
	    'XMI.CorbaTcBoolean': (self.start_XMI, self.end_XMI),
	    'XMI.CorbaTcEnum': (self.start_XMICorbaTcEnum, self.end_XMICorbaTcEnum),
	    'XMI.CorbaTcEnumLabel': (self.start_XMICorbaTcEnumLabel, self.end_XMICorbaTcEnumLabel),
	    'XMI.CorbaTcLong': (self.start_XMI, self.end_XMI),
	    'XMI.CorbaTcString': (self.start_XMI, self.end_XMI),
	    'XMI.CorbaTypeCode': (self.start_XMI, self.end_XMI),
	    'XMI.any': (self.start_XMI, self.end_XMI),
	    'XMI.content': (self.start_XMI, self.end_XMI),
	    'XMI.field': (self.start_XMIfield, self.end_XMIfield),
	    'XMI.header': (self.start_XMI, self.end_XMI),
	    'XMI.metamodel': (self.start_XMI, self.end_XMI),
	    'XMI.model': (self.start_XMI, self.end_XMI),
	    NS + 'Association': (self.start_Association, self.end_Association),
	    NS + 'AssociationEnd': (self.start_AssociationEnd, self.end_AssociationEnd),
	    NS + 'AssociationEnd.multiplicity': (self.start_multiplicity, self.end_multiplicity),
	    NS + 'Attribute': (self.start_Attribute, self.end_Attribute),
	    NS + 'Class': (self.start_Class, self.end_Class),
	    NS + 'DataType': (self.start_DataType, self.end_DataType),
	    NS + 'DataType.typeCode': (self.start_DataTypetypeCode, self.end_DataTypetypeCode),
	    NS + 'Import': (self.start_Import, self.end_Import),
	    NS + 'Namespace.contents': (self.start_Namespacecontents, self.end_Namespacecontents),
	    NS + 'Package': (self.start_Package, self.end_Package),
	    NS + 'Reference': (self.start_Reference, self.end_Reference),
	    NS + 'StructuralFeature.multiplicity': (self.start_multiplicity, self.end_multiplicity),
	    NS + 'Tag': (self.start_Tag, self.end_Tag),
	    NS + 'Tag.values': (self.start_Tagvalues, self.end_Tagvalues)
	}
	apply(XMLParser.__init__, (self,), kw)

    def push(self, val):
	self.mmstack.insert(0, val)

    def pop(self):
	val = self.mmstack[0]
	self.mmstack.remove(val)
	return val

    def peek(self):
	return self.mmstack[0]

    def handle_xml(self, encoding, standalone):
	pass

    def handle_doctype(self, tag, pubid, syslit, data):
	pass

    def start_XMI(self, data):
	pass
	# Skip XMI related stuff, not interesting

    def end_XMI(self):
	pass

    def start_Association(self, data):
	assert isinstance(self.peek(), Package)
	a = Association(id=data[NS + 'xmi.id'], name=data[NS + 'name'])
	self.peek().add_association(a)
	self.push(a)
	msg('a')

    def end_Association(self):
        self.pop()

    def start_AssociationEnd(self, data):
	assert isinstance(self.peek(), Association)
	ae = AssociationEnd(id=data[NS + 'xmi.id'],
	                    name=data[NS + 'name'],
			    type=data[NS + 'type'],
			    association=self.peek(),
			    isNavigable=data[NS + 'isNavigable'])
        self.peek().add_association_end(ae)
	self.push(ae)

    def end_AssociationEnd(self):
        self.pop()

    def start_Attribute(self, data):
	assert isinstance(self.peek(), Class)
	a = Attribute(id=data[NS + 'xmi.id'],
	              name=data[NS + 'name'],
		      type=data[NS + 'type'])
        self.peek().add_attribute(a)
	self.push(a)

    def end_Attribute(self):
        self.pop()

    def start_Class(self, data):
	assert isinstance(self.peek(), Package)
	if data.has_key(NS + 'supertypes'):
	    supertypes = data[NS + 'supertypes']
	else:
	    supertypes = None
	c = Class(id=data[NS + 'xmi.id'],
	          name=data[NS + 'name'],
		  isAbstract=data[NS + 'isAbstract'],
		  supertypes=supertypes)
	self.peek().add_class(c)
        self.push(c)
	msg('c')

    def end_Class(self):
        self.pop()

    def start_DataType(self, data):
	d = DataType(id=data[NS + 'xmi.id'], name=data[NS + 'name'])
	self.peek().add_datatype(d)
        self.push(d)
	msg('d')

    def end_DataType(self):
        self.pop()

    def start_DataTypetypeCode(self, data):
        pass

    def end_DataTypetypeCode(self):
        pass

    def start_XMICorbaTcEnum(self, data):
	assert isinstance(self.peek(), DataType)
        self.peek().is_enumeration()

    def end_XMICorbaTcEnum(self):
	pass

    def start_XMICorbaTcEnumLabel(self, data):
        self.peek().add_enumvalue(data['xmi.tcName'])

    def end_XMICorbaTcEnumLabel(self):
        pass

    def start_Import(self, data):
	assert isinstance(self.peek(), Package)
	i = Import(id=data[NS + 'xmi.id'],
	           name=data[NS + 'name'],
		   importedNamespace=data[NS + 'importedNamespace'])
	self.peek().add_import(i)
	self.push(i)
	msg('i')

    def end_Import(self):
        self.pop()

    def start_Namespacecontents(self, data):
	pass

    def end_Namespacecontents(self):
	pass

    def start_Package(self, data):
	p = Package(id=data[NS + 'xmi.id'],
		    name=data[NS + 'name'])
	msg('Parsing package: ' + data[NS + 'name'] + '\n ')
	self.push(p)

    def end_Package(self):
	self.pop()
	msg('\n')

    def start_Reference(self, data):
	r = Reference(id=data[NS + 'xmi.id'],
		      name=data[NS + 'name'],
		      type=data[NS + 'type'],
		      referencedEnd=data[NS + 'referencedEnd'])
	self.peek().add_reference(r)
	self.push(r)

    def end_Reference(self):
	self.pop()

    def start_multiplicity(self, data):
	assert isinstance(self.peek(), AssociationEnd) or isinstance(self.peek(), Attribute)
	self.multiplicity = []

    def end_multiplicity(self):
	m = Multiplicity(lower=int(self.multiplicity[0]),
	                 upper=int(self.multiplicity[1]),
	                 isOrdered=self.multiplicity[2],
			 isUnique=self.multiplicity[3])
	self.peek().set_multiplicity(m)
	del self.multiplicity

    def start_XMIfield(self, data):
	self.xmifield = ''

    def end_XMIfield(self):
	self.multiplicity.append(self.xmifield)
	self.xmifield = None

    def start_Tag(self, data): # skip this
	pass

    def end_Tag(self):
        pass

    def start_Tagvalues(self, data): # skip this
        pass

    def end_Tagvalues(self):
        pass

    def handle_data(self, data):
        "Handle normal data, is only inside XMI.field tags."
	if self.xmifield is not None:
	    self.xmifield = self.xmifield + data

    def handle_cdata(self, data):
	"Should not have CDATA."
	pass

    def handle_proc(self, name, data):
	"Should not have to need processing"
	pass

    def handle_comment(self, data):
	"Skip comments."
	pass

    def syntax_error(self, message):
        msg('error at line ' + self.lineno + ': ' +  message)

    def unknown_starttag(self, tag, attrs):
	msg ('*** UNKNOWN TAG: ' + tag)
	raise ValueException, tag + ' not supported.'

    def unknown_endtag(self, tag):
	pass

    def unknown_entityref(self, ref):
	msg('*** UNKNOWN ENTITYREF: &' + ref + ';')
	raise ValueException, tag + ' not supported.'

    def unknown_charref(self, ref):
	msg('*** UNKNOWN CHARREF: &#' + ref + ';')
	raise ValueException, tag + ' not supported.'

def generate(xmi_file, output_file=None):
    try:
	f = open(xmi_file, 'r')
    except IOError, e:
	msg (xmi_file, ':', e)
	sys.exit(1)

    data = f.read()
    if f is not sys.stdin:
	f.close()

    if output_file:
	try:
	   output  = open(output_file, 'w')
	   out = output.write
	except IOError, e:
	    msg (str(e))
	    sys.exit(1)
    else:
	out = sys.stdout.write

    parser = MetaModelParser()
    try:
	for c in data:
	    parser.feed(c)
	parser.close()
    except Error, e:
	msg(e)
	sys.exit(1)

    for e in elements.values():
	e.resolve_references()

    # TODO: Create extra references based on AssociationEnd's values.
    # Some AssociationEnds are not referenced from a Class by a Reference tag,
    # We can provide one, so the model can be more tight.
    # I don't know how this will affect double association names...
    def translate_names (name, a):
	"""For some reason, there are some names used double in the meta model.
	This function filters the double entries and gives them unique names or
	changes the navigability.
	name: name of the class
	a: association end that references the class
	"""
	try:
	    x = translations[name + '.' + a.name]
	    ass = x[0](a)
	    msg('[' + name + '.' + a.name + '] ' + ass.other_end().type.name + '.' + ass.name + ': ' + x[1] + ' := ' + str(x[2]) + '\n')
	    assert hasattr(ass, x[1])
	    ass.__dict__[x[1]] = x[2]
	except KeyError, e:
	    pass
		
    for p in filter(lambda p: isinstance(p, Package), elements.values()):
	for a in p.associations:
	    assert len(a.associationEnds) == 2
	    a1 = a.associationEnds[0]
	    a2 = a.associationEnds[1]
	    #if a1 not in a2.type.references:
	    #if a1.type.is_referenced(a2) or a2.type.is_referenced(a1):
	    a2.type.add_association_end(a1)
	    a1.type.add_association_end(a2)
	    translate_names(a1.type.name, a2)
	    translate_names(a2.type.name, a1)

    out('# MetaModel definition.\n')
    out('# This file is generated by genUML.py, do not edit.\n\n')
    out('import types\n')
    out('from element import Element, Sequence, Enum, Multiplicity\n')
    out('\n# Datatypes:\n')

    for d in filter(lambda e: isinstance(e, DataType), elements.values()):
	if d.name not in custom_elements:
	    out(d.str())

    out('\n# Class definitions:\n')

    done = [ ]
    for c in filter(lambda e: isinstance(e, Class) and e.name in custom_elements, elements.values()):
	done.append(c)

    for c in filter(lambda e: isinstance(e, Class), elements.values()):
	out(c.defstr(done)) # provide empty list

    out('\n# Class implementations:\n')
    for c in filter(lambda e: isinstance(e, Class), elements.values()):
	if c.name not in custom_elements:
	    out(c.implstr())

    if output_file:
	output.close()

if __name__ == '__main__':
    args = sys.argv[1:]

    if args:
	generate(args[0])
    else:
	msg('Usage: ' + sys.argv[0] + ' <UML MetaModel file.xmi>\nThe Python data model is written to stdout')
	sys.exit(1)

