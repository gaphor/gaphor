# vim:sw=4:et
from xml.sax import handler

class base(object):
    """Simple base class for element, canvas and canvasitem."""

    def __init__(self):
        self.values = { }
        self.references = { }

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

    def push(self, element):
        """Add an element to the item stack."""
        self.__stack.append(element)

    def pop(self):
        """Return the last item on the stack. The item is removed from
        the stack."""
        return self.__stack.pop()

    def peek(self):
        """Return the last item on the stack. The item is not removed."""
        return self.__stack[-1]

    def startDocument(self):
        """Start of document: all our attributes are initialized."""
        self.elements = {} # map id: element/canvasitem
        self.__stack = []
        self.value_is_cdata = 0
        self.cdata = ''
        # may have 3 states:
        #  2: simple data, should be stripped
        #  1: CDATA block,
        #  0: end CDATA, read no more data till the next element
        self.in_cdata = 0

    def endDocument(self):
        assert len(self.__stack) == 0, 'Invalid XML document.'

    def startElement(self, name, attrs):
        #print 'name:', name
        self.cdata = ''
        self.in_cdata = 2 # initial, just read text

        if name == 'Element':
            id = attrs['id']
            e = element(id, attrs['type'])
            self.elements[id] = e
            self.push(e)

        elif name == 'Canvas':
            c = canvas()
            self.peek().canvas = c
            self.push(c)

        elif name == 'CanvasItem':
            id = attrs['id']
            c = canvasitem(id, attrs['type'])
            self.elements[id] = c
            self.peek().canvasitems.append(c)
            self.push(c)

        elif name == 'Value':
            # Note that Value may contain CDATA
            v = attrs.get('value')
            if v:
                self.value_is_cdata = 0
                self.peek().values[attrs['name']] = v
            else:
                self.value_is_cdata = 1
                self.push(attrs['name'])

        elif name == 'Reference':
            # No data is pushed on the stack for references
            r = self.peek().references
            n = attrs['name']
            refid = attrs['refid']
            try:
                r[n].append(refid)
            except KeyError:
                r[n] = [refid]

        elif name == 'Gaphor':
            assert attrs['version'] == '1.1'
            self.push(None)

    def endElement(self, name):
        if name == 'Reference':
            pass # do nothing, stack should not be pop'ed.
        elif name == 'Value':
            if self.value_is_cdata:
                n = self.pop()
                #print '%s: "%s"' % (n, self.cdata)
                if self.in_cdata == 2:
                    self.cdata = self.cdata.strip()
                self.peek().values[n] = self.cdata
        else:
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
    """Parse a file and return a dictionary ID:element/canvasitem."""
    from xml.sax import make_parser
    parser = make_parser()

    ch = GaphorLoader()

    parser.setProperty(handler.property_lexical_handler, ch)
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(ch)

    parser.parse(filename)
    #parser.close()
    return ch.elements

if __name__ == '__main__':
    parse('ns.xml')
    #parser.parse('ns2.xml')
    print len(ch.elements)
