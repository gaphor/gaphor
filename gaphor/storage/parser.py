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
from __future__ import division

from builtins import range
from past.utils import old_div
__all__ = [ 'parse', 'ParserException' ]

import os
import types
from xml.sax import handler
from cStringIO import InputType

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

    def __init__(self, id, type):
        base.__init__(self)
        self.id = id
        self.type = type
        self.canvas = None

class canvas(base):

    def __init__(self):
        base.__init__(self)
        self.canvasitems = []

class canvasitem(base):

    def __init__(self, id, type):
        base.__init__(self)
        self.id = id
        self.type = type
        self.canvasitems = []


XMLNS='http://gaphor.sourceforge.net/model'

class ParserException(Exception):
    pass


# Loader state:
[ROOT,         # Expect 'gaphor' element
 GAPHOR,       # Expect UML classes (tag name is the UML class name)
 ELEMENT,      # Expect properties of UML object
 DIAGRAM,      # Expect properties of Diagram object + canvas
 CANVAS,       # Expect canvas properties + <item> tags
 ITEM,         # Expect item attributes and nested items
 ATTR,         # Reading contents of an attribute (such as a <val> or <ref>)
 VAL,          # Redaing contents of a <val> tag
 REFLIST,      # In a <reflist>
 REF           # Reading contents of a <ref> tag
 ] = range(10)

class GaphorLoader(handler.ContentHandler):
    """Create a list of elements. an element may contain a canvas and a
    canvas may contain canvas items. Each element can have values and
    references to other elements.
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
        self.text = ''

    def endDocument(self):
        if len(self.__stack) != 0:
            raise ParserException('Invalid XML document.')

    def startElement(self, name, attrs):
        self.text = ''

        state = self.state()

        # Read a element class. The name of the tag is the class name:
        if state == GAPHOR:
            id = attrs['id']
            e = element(id, name)
            assert id not in list(self.elements.keys()), '%s already defined' % (id)#, self.elements[id])
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
            assert id not in list(self.elements.keys()), '%s already defined' % id
            self.elements[id] = c
            self.peek().canvasitems.append(c)
            self.push(c, ITEM)

        # Store the attribute name on the stack, so we can use it later
        # to store the <ref>, <reflist> or <val> content:
        elif state in (ELEMENT, DIAGRAM, CANVAS, ITEM):
            # handle 'normal' attributes
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
            raise ParserException('Invalid XML: tag <%s> not known (state = %s)' % (name, state))

    def endElement(self, name):
        # Put the text on the value
        if self.state() == VAL:
            # Two levels up: the attribute name
            n = self.peek(2)
            # Three levels up: the element instance (element or canvasitem)
            self.peek(3).values[n] = self.text
        self.pop()

    def startElementNS(self, name, qname, attrs):
        if not name[0] or name[0] == XMLNS:
            a = { }
            for key, val in list(attrs.items()):
                a[key[1]] = val
            self.startElement(name[1], a)

    def endElementNS(self, name, qname):
        if not name[0] or name[0] == XMLNS:
            self.endElement(name[1])

    def characters(self, content):
        """Read characters."""
        self.text = self.text + content


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

    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(loader)

    for percentage in parse_file(filename, parser):
        yield percentage


class ProgressGenerator(object):
    """A generator that yields the progress of taking from a file input object 
    and feeding it into an output object.  The supplied file object is neither
    opened not closed by this generator.  The file object is assumed to
    already be opened for reading and that it will be closed elsewhere."""

    def __init__(self, input, output, block_size=512):
        """Initialize the progress generator.  The input parameter is a file
        object.  The ouput parameter is usually a SAX parser but can be 
        anything that implements a feed() method.  The block size is the size
        of each block that is read from the input."""

        self.input = input
        self.output = output
        self.block_size = block_size
        if isinstance(self.input, types.FileType):
            self.file_size = os.fstat(self.input.fileno())[6]
        elif isinstance(self.input, InputType):
            self.file_size = len(self.input.getvalue())
            self.input.reset()

    def __iter__(self):
        """Return a generator that yields the progress of reading data
        from the input and feeding it into the output.  The progress
        yielded in each iteration is the percentage of data read, relative
        to the to input file size."""

        block = self.input.read(self.block_size)
        read_size = len(block)

        while block:
            self.output.feed(block)
            block = self.input.read(self.block_size)
            read_size += len(block)
            yield old_div((read_size * 100), self.file_size)


def parse_file(filename, parser):
    """Parse the supplied file using the supplied parser.  The parser parameter
    should be a GaphorLoader instance.  The filename parameter can be an
    open file descriptor instance or the name of a file.  The progress
    percentage of the parser is yielded."""

    is_fd = True

    if isinstance(filename, (types.FileType, InputType)):
        file_obj = filename
    else:
        is_fd = False
        file_obj = open(filename, 'rb')

    for progress in ProgressGenerator(file_obj, parser):
        yield progress

    parser.close()

    if not is_fd:
        file_obj.close()

# vim:sw=4:et:ai
