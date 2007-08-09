# vim:sw=4:et
"""Gaphor file reader.

This module contains only one interesting function:

    parse(filename)

which returns a dictionary of ID -> <parsed_object> pairs.

A parsed_object is one of element, canvas or canvasitem.

A parsed_object contains values and references. values is a dictionary of
name -> value pairs. A value contains a string with the value read from the
model file. references contains a list of name -> reference_list pairs, where
reference_list is a list of ID's.

element objects can contain a canvas object (which is the case for elements
of type Diagram). Each element has a type, which corresponds to a class name
in the gaphor.UML module. Elements also have a unique ID, by which they are
referered to in the dictionary returned by parse().

canvas does not have an ID, but contains a list of canvasitems (which is a
list of real canvasitem objects, not references).

canvasitem objects can also contain a list of canvasitems (canvasitems can be
nested). They also have a unique ID by which they have been added to the
dictionary returned by parse(). Each canvasitem has a type, which maps to a
class name in the gaphor.diagram module.

The generator parse_generator(filename, loader) may be used if the loading
takes a long time. The yielded values are the percentage of the file read.
"""

__all__ = [ 'parse', 'ParserException' ]

import os
from xml.sax import handler

from gaphor.misc.odict import odict

class base(object):
    """Simple base class for element, canvas and canvasitem.
    """

    def __init__(self):
        self.values = { }
        self.references = { }

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        try:
            return self.values[key]
        except:
            return self.references[key]

    def get(self, key):
        try:
            return self.__getitem__(key)
        except:
            return None

class element(base):
    #__slots__ = ('id', 'type', 'canvas', 'values', 'references')

    def __init__(self, id, type):
        base.__init__(self)
        self.id = id
        self.type = type
        self.canvas = None

class canvas(base):
    #__slots__ = ('canvasitems', 'values', 'references')

    def __init__(self):
        base.__init__(self)
        self.canvasitems = []

class canvasitem(base):
    #__slots__ = ('id', 'type', 'canvasitems', 'values', 'references')

    def __init__(self, id, type):
        base.__init__(self)
        self.id = id
        self.type = type
        self.canvasitems = []


XMLNS='http://gaphor.sourceforge.net/gaphor'

class ParserException(Exception):
    pass

# Loader state:
[ ROOT,         # Expect 'gaphor' element
  GAPHOR,       # Expect UML classes (tag name is the UML class name)
  ELEMENT,      # Expect properties of UML object
  DIAGRAM,      # Expect properties of Diagram object + canvas
  CANVAS,       # Expect canvas properties + <item> tags
  ITEM,         # Expect item attributes and nested items
  ATTR,         # Reading contents of an attribute (such as a <val> or <ref>)
  VAL,          # Redaing contents of a <val> tag
  REFLIST,      # In a <reflist>
  REF           # Reading contents of a <ref> tag
] = xrange(10)

class GaphorLoader(handler.ContentHandler):
    """Create a list of elements. an element may contain a canvas and a
    canvas may contain canvas items. Each element can have values and
    references to other elements.

    Data read in non-CDATA text is stripped. If a CDATA section is found all
    non-CDATA text is ignored.
    """

    def __init__(self):
        handler.ContentHandler.__init__(self)
        # make sure all variables are initialized:
        self.startDocument()

    def push(self, element, state):
        """Add an element to the item stack.
        """
        self.__stack.append((element, state))

    def pop(self):
        """Return the last item on the stack. The item is removed from
        the stack.
        """
        return self.__stack.pop()[0]

    def peek(self, depth=1):
        """Return the last item on the stack. The item is not removed.
        """
        return self.__stack[-1 * depth][0]

    def state(self):
        """Return the current state of the parser.
        """
        try:
            return self.__stack[-1][1]
        except IndexError:
            return ROOT

    def endDTD(self):
        pass

    def startDocument(self):
        """Start of document: all our attributes are initialized.
        """
        self.version = None
        self.gaphor_version = None
        self.elements = odict() # map id: element/canvasitem
        self.__stack = []
        self.value_is_cdata = 0
        self.cdata = ''
        # may have 3 states:
        #  2: simple data, should be stripped
        #  1: CDATA block,
        #  0: end CDATA, read no more data till the next element
        self.in_cdata = 0

    def endDocument(self):
        if len(self.__stack) != 0:
            raise ParserException, 'Invalid XML document.'

    def startElement(self, name, attrs):
        self.cdata = ''
        self.in_cdata = 2 # initial, just read text
        
        state = self.state()

        # Read a element class. The name of the tag is the class name:
        if state == GAPHOR:
            id = attrs['id']
            e = element(id, name)
            assert id not in self.elements.keys(), '%s already defined' % (id)#, self.elements[id])
            self.elements[id] = e
            self.push(e, name == 'Diagram' and DIAGRAM or ELEMENT)

        # Special treatment for the <canvas> tag in a Diagram:
        elif state == DIAGRAM and name == 'canvas':
            c = canvas()
            self.peek().canvas = c
            self.push(c, CANVAS)

        # Items in a canvas are referenced by the <item> tag:
        elif state in (CANVAS, ITEM) and name == 'item':
            id = attrs['id']
            c = canvasitem(id, attrs['type'])
            assert id not in self.elements.keys(), '%s already defined' % (id) #, self.elements[id])
            self.elements[id] = c
            self.peek().canvasitems.append(c)
            self.push(c, ITEM)

        # Store the attribute name on the stack, so we can use it later
        # to store the <ref>, <reflist> or <val> content:
        elif state in (ELEMENT, DIAGRAM, CANVAS, ITEM):
            # handle 'normal' attributes
            # Note that Value may contain CDATA
            self.push(name, ATTR)

        # Reference list:
        elif state == ATTR and name == 'reflist':
            self.push(self.peek(), REFLIST)

        # Reference with multiplicity 1:
        elif state  == ATTR and name == 'ref':
            n = self.peek(1)
            # Fetch the element instance from the stack
            r = self.peek(2).references[n] = attrs['refid']
            self.push(None, REF)

        # Reference with multiplicity *:
        elif state == REFLIST and name == 'ref':
            n = self.peek(1)
            # Fetch the element instance from the stack
            r = self.peek(3).references
            refid = attrs['refid']
            try:
                r[n].append(refid)
            except KeyError:
                r[n] = [refid]
            self.push(None, REF)

        # We need to get the text within the <val> tag:
        elif state == ATTR and name == 'val':
            self.value_is_cdata = 1
            self.push(None, VAL)

        # The <gaphor> tag is the toplevel tag:
        elif state == ROOT and name == 'gaphor':
            assert attrs['version'] in ('3.0',)
            self.version = attrs['version']
            self.gaphor_version = attrs.get('gaphor-version')
            if not self.gaphor_version:
                self.gaphor_version = attrs.get('gaphor_version')
            self.push(None, GAPHOR)

        else:
            raise ParserException, 'Invalid XML: tag <%s> not known (state = %s)' % (name, state)

    def endElement(self, name):
        # Put the text on the value
        if self.state() == VAL:
            if self.value_is_cdata:
                # Two levels up: the attribute name
                n = self.peek(2)
                if self.in_cdata == 2:
                    self.cdata = self.cdata.strip()
                # Three levels up: the element instance (element or canvasitem)
                self.peek(3).values[n] = self.cdata
        self.pop()

    def startElementNS(self, name, qname, attrs):
        #print 'name=', name
        #print 'qname=', qname
        #print 'attrs=', attrs
        if not name[0] or name[0] == XMLNS:
            a = { }
            for key, val in attrs.items():
                a[key[1]] = val
            self.startElement(name[1], a)

    def endElementNS(self, name, qname):
        if not name[0] or name[0] == XMLNS:
            self.endElement(name[1])

    def characters(self, content):
        """Read characters."""
        if self.in_cdata:
            self.cdata = self.cdata + content
            #print 'characters: "%s"' % self.cdata

    # Lexical handler stuff:

    def comment(self, comment):
        #print 'comment: "%s"' % comment
        pass

    def startCDATA(self):
        """Start a CDATA section. In case no CDATA section has been read
        before, the self.cdata is cleared."""
        if self.in_cdata == 2:
            self.cdata = ''
        self.in_cdata = 1

    def endCDATA(self):
        """End of CDATA section. No more data is read, unless another CDATA
        section is opened."""
        self.in_cdata = 0


def parse(filename):
    """Parse a file and return a dictionary ID:element/canvasitem.
    """
    loader = GaphorLoader()

    for x in parse_generator(filename, loader):
        pass
    return loader.elements


def parse_generator(filename, loader):
    """The generator based version of parse().
    parses the file filename and load it with ContentHandler loader.
    """
    assert isinstance(loader, GaphorLoader), 'loader should be a GaphorLoader'
    from xml.sax import make_parser
    parser = make_parser()

    parser.setProperty(handler.property_lexical_handler, loader)
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(loader)

    for percentage in parse_file(filename, parser):
        yield percentage


def parse_file(filename, parser):
    """Parse the file filename with parser.
    """
    file_size = os.stat(filename)[6]
    f = open(filename, 'rb')
    block_size = 512

    block = f.read(block_size)
    read_size = len(block)
    while block:
        parser.feed(block)
        block = f.read(block_size)
        read_size = read_size + len(block)
        yield (read_size * 100) / file_size

    parser.close()
    f.close()

if __name__ == '__main__':
    parse('ns.xml')
    #parser.parse('ns2.xml')
    #print len(ch.elements)
