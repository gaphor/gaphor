# vim: sw=4
'''management.py
This module contains some functions for managing UML models. This
includes saving, loading and flushing models. In the future things like
consistency checking should also be included.'''

import ModelElements as UML
import diagram
from xmllib import XMLParser
from xml.dom.minidom import Document

# Somehow I did not manage it to use the minidom/SAX stuff to create a
# decent parser, do I use this depricated (but workin ;) peace of code...
# The GaphorParser reads a Gaphor file and creates a DOM representation of
# the file.
class GaphorParser (XMLParser):
    '''GaphorParser
    The GaphorParser examines an inut strream and creates a Document object
    using the elements found in the XML file. The only restruction that we
    test is the Gaphor tag and the version (currently only 1.0)'''
    def __init__ (self, **kw):
	self.doit = 0
	self.doc = Document()
	self.elements = { 'Gaphor': (self.start_Gaphor, self.end_Gaphor) }
	self.__stack = [ ]
	apply(XMLParser.__init__, (self,), kw)

    def syntax_error(self, message):
	raise IOError, "XML document contains syntax errors: " + message

    def start_Gaphor (self, attrs):
	if attrs['version'] != '1.0':
	    raise Exception, 'Wrong version of Gaphor (' + \
			     attrs['version'] + ')'
	else:
	    node = self.doc.createElement('Gaphor')
	    self.doc.appendChild (node)
	    self.__stack.append (node)
	    self.doit += 1

    def end_Gaphor (self):
	self.doit -= 1

    def unknown_starttag(self, tag, attrs):
	if self.doit:
	    node = self.doc.createElement(tag)
	    self.__stack[-1].appendChild (node)
	    self.__stack.append (node)
	    for key in attrs.keys():
		node.setAttribute (key, attrs[key])

    def unknown_endtag(self, tag):
	self.__stack = self.__stack[:-1]

    def handle_cdata(self, tag):
	cdata = self.doc.createCDATASection (tag)
	self.__stack[-1].appendChild (cdata)

    def unknown_entityref(self, ref):
	raise ValueError, tag + " not supported."

    def unknown_charref(self, ref):
	raise ValueError, tag + " not supported."

def save (filename=None):
    document = Document()
    rootnode = document.createElement ('Gaphor')
    document.appendChild (rootnode)
    rootnode.setAttribute ('version', '1.0')
    for e in UML.elements.values():
	print 'Saving object', e
        e.save(document, rootnode)

    if not filename:
	print document.toxml(indent='  ', newl='\n')
    else:
    	file = open (filename, 'w')
	if not file:
	    raise IOError, 'Could not open file `%s\'' % (filename)
	document.writexml (file, indent='', addindent='  ', newl='\n')
	file.close()

def load (filename):
    '''Load a file and create a model if possible.
    Exceptions: IOError, ValueError.'''
    parser = GaphorParser()

    f = open (filename, 'r')
    while 1:
	data = f.read(512)
	parser.feed (data)
	if len(data) != 512:
	    break;
    parser.close()
    f.close()
     
    # Now iterate over the tree and create every element in the UML.elements
    # table.
    rootnode = parser.doc.firstChild
    for node in rootnode.childNodes:
	try:
	    if node.tagName == 'Diagram':
		cls = getattr (diagram, node.tagName)
	    else:
		cls = getattr (UML, node.tagName)
	except:
	    raise ValueError, 'Invalid field in Gaphor file: ' + node.tagName
	id = int (node.getAttribute('id'))
	old_index = UML.Element._index
	UML.Element._index = id
	cls()
	if old_index > id:
	    UML.Element._index = old_index
        #print node.tagName, node.getAttribute('id')

    # Second step: call Element.load() for every object in the element hash.
    # We also provide the XML node, so it can recreate it's state
    for node in rootnode.childNodes:
	id = int (node.getAttribute('id'))
	element = UML.lookup (id)
	assert element != None
	element.load (node)


def flush():
    '''Flush all elements in the UML.elements'''
    while 1:
	try:
	    (key, value) = UML.elements.popitem()
	except KeyError:
	    break;
	value.unlink()
    UML.elements.clear()
