#!/usr/bin/env python
# vim: sw=4
# MetaModel Parser: Parse the UML metamodel definition version 1.3 file
# as defined by the OMG.
#
# This script will produce the following files:
#	Activity_Graphs.py
#	Collaborations.py
#	Common_Behavior.py
#	Core.py
#	Data_Types.py
#	Model_Management.py
#	State_Machines.py
#	UML.py
#	Use_Cases.py
#	Enum_Types.py (part of Data_Types.py: contains the enumerations)
#
# Note that the output is written to STDOUT and the status messages and errors
# are written to STDERR.

import sys, getopt
from xmllib import *
import types

msg = sys.stderr.write

default_values = {
    "Name": "''",
    "Boolean": "0",
    "VisibilityKind": "VK_PUBLIC",
    "OrderingKind": "OK_UNORDERED",
    "ChangeableKind": "CK_CHANGEABLE",
    "ScopeKind": "SK_INSTANCE",
    "PseudostateKind": "PK_CHOICE",
    "ParameterDirectionKind": "PDK_IN",
    "AggregationKind": "AK_NONE",
    "CallConcurrencyKind": "CCK_SEQUENTIAL",
    "Expression": "None",
    "ActionExpression": "None",
    "IterationExpression": "None",
    "MappingExpression": "None",
    "BooleanExpression": "None",
    "TimeExpression": "None",
    "TypeExpression": "None",
    "ObjectSetExpression": "None",
    "ProcedureExpression": "None",
    "ArgListsExpression": "None",
    "Multiplicity": "1", # Defaults to Int
    "Integer": "1", # Defaults to Int
    "UnlimitedInteger": "1", # Defaults to Long
    "String": "''", # Defaults to String
    "Geometry": "None", # Defaults to a list (of length 4)
    "LocationReference": "None"
}

# For those classes no class definition is generated:
custom_elements = [
    "Element",
]

# These are some dictionaries where the objects are stored in. Package contains
# the top level objects. All other dictionaries are just for ease of lookup.
packages = { }
datatypes = { }
classes = { }
associations = { }

# UML 1.3 namespace:
NS='omg.org/mof.Model/1.3 '

# This is the parser. It's a bit hackish and maybe it only works for the
# UML 1.3 MetaModel (which is enough actually). The parser is stack based:
# for packages, classes, datatypes and associatiions new maps are created.
class MetaModelParser(XMLParser):

    def __init__(self, **kw):
	self.__level = [ ]
	self.xmifield = None
	# These are the elements we can expect in the MetaModel:
	self.elements = {
	    "XMI": (self.start_XMI, self.end_XMI),
	    "XMI.CorbaTcAlias": (self.start_XMI, self.end_XMI),
	    "XMI.CorbaTcBoolean": (self.start_XMI, self.end_XMI),
	    "XMI.CorbaTcEnum": (self.start_XMICorbaTcEnum, self.end_XMICorbaTcEnum),
	    "XMI.CorbaTcEnumLabel": (self.start_XMICorbaTcEnumLabel, self.end_XMICorbaTcEnumLabel),
	    "XMI.CorbaTcLong": (self.start_XMI, self.end_XMI),
	    "XMI.CorbaTcString": (self.start_XMI, self.end_XMI),
	    "XMI.CorbaTypeCode": (self.start_XMI, self.end_XMI),
	    "XMI.any": (self.start_XMI, self.end_XMI),
	    "XMI.content": (self.start_XMI, self.end_XMI),
	    "XMI.field": (self.start_XMIfield, self.end_XMIfield),
	    "XMI.header": (self.start_XMI, self.end_XMI),
	    "XMI.metamodel": (self.start_XMI, self.end_XMI),
	    "XMI.model": (self.start_XMI, self.end_XMI),
	    "omg.org/mof.Model/1.3 Association": (self.start_Association, self.end_Association),
	    "omg.org/mof.Model/1.3 AssociationEnd": (self.start_AssociationEnd, self.end_AssociationEnd),
	    "omg.org/mof.Model/1.3 AssociationEnd.multiplicity": (self.start_multiplicity, self.end_multiplicity),
	    "omg.org/mof.Model/1.3 Attribute": (self.start_Attribute, self.end_Attribute),
	    "omg.org/mof.Model/1.3 Class": (self.start_Class, self.end_Class),
	    "omg.org/mof.Model/1.3 DataType": (self.start_DataType, self.end_DataType),
	    "omg.org/mof.Model/1.3 DataType.typeCode": (self.start_DataTypetypeCode, self.end_DataTypetypeCode),
	    "omg.org/mof.Model/1.3 Import": (self.start_Import, self.end_Import),
	    "omg.org/mof.Model/1.3 Namespace.contents": (self.start_Namespacecontents, self.end_Namespacecontents),
	    "omg.org/mof.Model/1.3 Package": (self.start_Package, self.end_Package),
	    "omg.org/mof.Model/1.3 Reference": (self.start_Reference, self.end_Reference),
	    "omg.org/mof.Model/1.3 StructuralFeature.multiplicity": (self.start_multiplicity, self.end_multiplicity),
	    "omg.org/mof.Model/1.3 Tag": (self.start_Tag, self.end_Tag),
	    "omg.org/mof.Model/1.3 Tag.values": (self.start_Tagvalues, self.end_Tagvalues)
	}
	apply(XMLParser.__init__, (self,), kw)

    def level(self):
        return self.__level[0]

    def inc_level(self, dict):
	if len (self.__level) > 0:
	    self.__level[0][dict['id']] = dict
        self.__level.insert(0, dict)

    def dec_level(self):
        self.__level.pop(0)

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
	dict = {"tag": "association",
		"id": data[NS + "xmi.id"],
		"name": data[NS + "name"] } 
	associations[dict['id']] = dict
	self.inc_level(dict)
	msg("a")

    def end_Association(self):
        self.dec_level()

    def start_AssociationEnd(self, data):
	dict = {"tag": "associationend",
		"id": data[NS + "xmi.id"],
		"name": data[NS + "name"],
		"type": data[NS + "type"],
		"aggregation": data[NS + "aggregation"] } 
        self.inc_level(dict)

    def end_AssociationEnd(self):
        self.dec_level()

    def start_Attribute(self, data):
	dict = {"tag": "attribute",
		"name": data[NS + "name"],
		"id": data[NS + "xmi.id"],
		"type": data[NS + "type"] }
        self.inc_level(dict)

    def end_Attribute(self):
        self.dec_level()

    def start_Class(self, data):
	dict = {"tag": "class",
		"name": data[NS + "name"],
		"id": data[NS + "xmi.id"] }
	if data.has_key(NS + "supertypes"):
		dict["supertypes"] = data[NS + "supertypes"]
	classes[dict['id']] = dict
        self.inc_level(dict)
	msg("c")

    def end_Class(self):
        self.dec_level()

    def start_DataType(self, data):
	dict = {"tag": "datatype",
		"name": data[NS + "name"],
		"id": data[NS + "xmi.id"] }
	datatypes[dict['id']] = dict
        self.inc_level(dict)
	msg("d")

    def end_DataType(self):
        self.dec_level()

    def start_DataTypetypeCode(self, data):
        pass

    def end_DataTypetypeCode(self):
        pass

    def start_XMICorbaTcEnum(self, data):
        self.enumlabel = [ ]

    def end_XMICorbaTcEnum(self):
        self.level()["enumeration"] = self.enumlabel

    def start_XMICorbaTcEnumLabel(self, data):
        self.enumlabel.append(data["xmi.tcName"])

    def end_XMICorbaTcEnumLabel(self):
        pass

    def start_Import(self, data):
	dict = {"tag": "import",
		"name": data[NS + "name"],
		"id": data[NS + "xmi.id"],
		"importedNamespace": data[NS + "importedNamespace"] }
        self.inc_level(dict)

    def end_Import(self):
        self.dec_level()

    def start_Namespacecontents(self, data):
	pass

    def end_Namespacecontents(self):
	pass

    def start_Package(self, data):
	dict = {"tag": "package",
		"id": data[NS + "xmi.id"],
		"name": data[NS +"name"] }
	packages[dict['id']] = dict
        self.inc_level(dict)
	msg("Parsing package: " + dict['name'] + "\n ")

    def end_Package(self):
	self.dec_level()
	msg("\n")

    def start_Reference(self, data):
	dict = {"tag": "reference",
		"id": data[NS + "xmi.id"],
		"name": data[NS + "name"],
		"type": data[NS + "type"],
		"referencedEnd": data[NS + "referencedEnd"] }
	self.inc_level(dict)

    def end_Reference(self):
	self.dec_level()

    def start_multiplicity(self, data):
	self.multiplicity = []

    def end_multiplicity(self):
	self.level()['lower'] = int(self.multiplicity[0])
	self.level()['upper'] = int(self.multiplicity[1])
	self.level()['is_ordered'] = self.multiplicity[2] == "true"
	self.level()['is_unique'] = self.multiplicity[3] == "true"

    def start_XMIfield(self, data):
	self.xmifield = ""

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

    def handle_proc(self, name, data):
	"Should not have to need processing"

    def handle_comment(self, data):
	"Skip comments."

    def syntax_error(self, message):
        msg('error at line ' + self.lineno + ': ' +  message)

    def unknown_starttag(self, tag, attrs):
	msg ('*** UNKNOWN TAG: ' + tag)
	raise ValueException, tag + " not supported."

    def unknown_endtag(self, tag):
	pass

    def unknown_entityref(self, ref):
	msg('*** UNKNOWN ENTITYREF: &' + ref + ';')
	raise ValueException, tag + " not supported."

    def unknown_charref(self, ref):
	msg('*** UNKNOWN CHARREF: &#' + ref + ';')
	raise ValueException, tag + " not supported."

#####
##### Start of the execution
#####

args = sys.argv[1:]

if args:
    file = args[0]
else:
    msg("Usage: " + sys.argv[0] + " <UML MetaModel file.xmi>\n")
    sys.exit(1)

try:
    f = open(file, 'r')
except IOError, e:
    msg (file, ":", e)
    sys.exit(1)

data = f.read()
if f is not sys.stdin:
    f.close()

parser = MetaModelParser()
try:
    for c in data:
	parser.feed(c)
    parser.close()
except Error, e:
    msg(e)
    sys.exit(1)

# At this point we have parsed the .XMI file and we can now construct the
# data that has to be written to the <PackageName>.py files
# The 'packages' map now has the structure:
# a0:
#	a15:
#		importedNamespace: a16
#		tag: import
#		name: Activity_Graphs
#		id: a15
#	name: UML
#	tag: package
#	a??:
#		tag: association
#		a??:
#			tag: associationend
#	...
#
# The first thing we do is create a new map ('out') which contains all classes
# in the package. All attributes and associations are added to the class map.
# After that we use it to construct a file called <package>.py. This file
# is written in proper Python and should work without any further code.
# All produced files depend on Element.py. The Element contains
# code that checks the class' '_attrdef' structure and checks the type of class
# that is to be assigned to the class.

#try:
#    f = open('UML.py', 'w')
#except IOError, e:
#    msg(file, ":", e)
#    sys.exit(1)
f = sys.stdout
out = f.write

msg("Writing definitions...")

# Header and import statements
out("# MetaModel definition.\n")
out("# This file is generated, do not edit.\n")
out("\n")
out("import types\n")
out("from element import *\n")
out("\n# Enumeration types:\n")

cnt = 0
for key in datatypes.keys():
    # If we have an enumeration type, define them:
    if datatypes[key].has_key("enumeration"):
	out("\n")
	for enum in datatypes[key]["enumeration"]:
	    out(enum.upper() + " = '" + enum + "'\n")
	out("class " + datatypes[key]["name"] + "(Enumeration_):\n")
	out("    _values = [ ")
	for enum in datatypes[key]["enumeration"]:
	    out(enum.upper() + ", ")
	out("]\n")
	cnt += 1

msg("Wrote " + str(cnt) + " enumeration types.\n")

out("\n# Class definitions:\n")

# First write class definitions:
cnt = 0
done = { }

# Create all class definitions. We should create them in the right order,
# otherwise the interpreter will error.
def write_class(key):
    global cnt
    if classes.has_key(key) and not done.has_key(key):
	if classes[key]["name"] in custom_elements:
	    return
	# Examine supertypes 
	if classes[key].has_key("supertypes"):
	    super = [ ]
	    for s in classes[key]["supertypes"].split(' '):
		super.append(classes[s]["name"])
		if not done.has_key(s):
		    write_class(s)

	    # Now add yourself:
	    out("class " + classes[key]["name"] + "(" + super[0])
	    for i in xrange (1, len(super)):
		out(", " + super[i])
	    out("): _attrdef = { }\n")
	else:	
	    out("class " + classes[key]["name"] + "(Element): _attrdef = { }\n")
	done[key] = 0
	cnt += 1

for key in classes.keys():
    write_class(key)

del done

msg("Wrote " + str(cnt)  + " class definitions.\n")

out("\n# Attributes:\n")
cnt = 0

# Examine attributes
for cls in classes.keys():
    cls_name = classes[cls]["name"]
    for attr in classes[cls].keys():
	the_attr = classes[cls][attr]
	if isinstance (the_attr, types.DictType) and the_attr["tag"] == "attribute":
	    if classes.has_key(the_attr["type"]):
		out(cls_name + "._attrdef['" + the_attr["name"] + "'] = ( " + default_values[classes[the_attr["type"]]["name"]] + ", " + classes[the_attr["type"]]["name"] + " )\n")
	    elif datatypes.has_key(the_attr["type"]):
		out(cls_name + "._attrdef['" + the_attr["name"] + "'] = ( " + default_values[datatypes[the_attr["type"]]["name"]] + ", " + datatypes[the_attr["type"]]["name"] + " )\n")
	    else:
		raise ValueError, "Unknown tag: " + the_attr["type"]
	    cnt += 1

msg("Wrote " + str(cnt) + " attribute definitions.\n")

out("\n# Associations, ordered by pair\n")

# And at last add associations:
cnt = 0
def write_assoc(assend1, assend2):
    global cnt
    
    def is_referenced(cls, id):
	for key in cls.keys():
	    the_rel = cls[key]
	    if isinstance (the_rel, types.DictType) and the_rel["tag"] == "reference" and the_rel["referencedEnd"] == id:
		return 1
	return 0

    if classes[assend1["type"]]["name"] not in custom_elements:
	mult = 'None'
	if assend2["upper"] == -1: # multiplicity = '*'
	    mult = 'Sequence'
        if is_referenced(classes[assend2["type"]], assend1["id"]) \
	    or is_referenced(classes[assend1["type"]], assend2["id"]):
	    out(classes[assend1["type"]]["name"] + "._attrdef['" + \
			assend2["name"] + "'] = ( " + mult + ", " + \
			classes[assend2["type"]]["name"] + ", '" + \
			assend1["name"] + "' )\n")
	else:
	    out(classes[assend1["type"]]["name"] + "._attrdef['" + \
			assend2["name"] + "'] = ( " + mult + ", " + \
			classes[assend2["type"]]["name"] + " )\n")
	cnt += 1

for ass in associations.keys():
    the_ass = associations[ass]
    if isinstance (the_ass, types.DictType) and the_ass["tag"] == "association":
	assend1 = None
	assend2 = None
	for assend in the_ass.keys():
	    the_assend = the_ass[assend]
	    if isinstance (the_assend, types.DictType) and the_assend["tag"] == "associationend":
		if assend1 is None:
		    assend1 = the_assend
		else:
		    assend2 = the_assend

	write_assoc(assend1, assend2)
	write_assoc(assend2, assend1)

msg ("Wrote " + str(cnt) + " associations.\n")

if f is not sys.stdout:
    f.close()

