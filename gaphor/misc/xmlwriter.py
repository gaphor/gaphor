# vim:sw=4:et

import sys
from xml.sax.saxutils import XMLGenerator


class XMLWriter(XMLGenerator):
    """An XMLGenerator with CDATA handling extensions.
    """

    def __init__(self, out=None):
        XMLGenerator.__init__(self, out, sys.getdefaultencoding())
        self._in_cdata = False
        self._in_start_tag = False

    def _write(self, text, raw=False):
        """
        This write method is a bit smart about what it writes.
        ``raw`` can be set to True to circumvent the smart behaviour.
        """
        # We have an end tag:
        if not raw and self._in_start_tag and text.startswith('</'):
            XMLGenerator._write(self, '/>')
            self._in_start_tag = False
            return
           
        # A normal start tag: remember we didn't write it
        if not raw and text == '>':
            self._in_start_tag = True
            return

        # close last start tag:
        if self._in_start_tag:
            XMLGenerator._write(self, '>')

        # starting a new tag: add newlines
        if not raw and text.startswith('<') and not text.startswith('</') and not text.startswith('<?') and not text.startswith('<%'):
            XMLGenerator._write(self, '\n')
            
        self._in_start_tag = False
        XMLGenerator._write(self, text)

    # Lexical handler methods

    def startDocument(self):
        self._write('<?xml version="1.0" encoding="%s"?>' %
                        self._encoding)

#    def startElement(self, name, attrs):
#        self._write('\n')
#        self._write('<' + name)
#        for (name, value) in attrs.items():
#            self._write(' %s=%s' % (name, quoteattr(value)))
#        self._in_start_tag = True

#    def endElement(self, name):
#        if self._in_start_tag:
#            self._in_start_tag = False
#            self._write('/>')
#        else:
#            XMLGenerator.endElement(self, name)
#        self._write('\n')
 
#    def startElementNS(self, name, qname, attrs):
#        self._write('\n')
#        self._write('<' + self._qname(name))
#
#        for prefix, uri in self._undeclared_ns_maps:
#            if prefix:
#                self._out.write(' xmlns:%s="%s"' % (prefix, uri))
#            else:
#                self._out.write(' xmlns="%s"' % uri)
#        self._undeclared_ns_maps = []
#
#        for (name, value) in attrs.items():
#            self._write(' %s=%s' % (self._qname(name), quoteattr(value)))
#        self._in_start_tag = True

#    def endElementNS(self, name, qname):
#        """
#        Like XMLGenerator.endElementNS(), but adds newline at end of tag.
#        """
#        if self._in_start_tag:
#            self._in_start_tag = False
#            self._write('/>')
#        else:
#            XMLGenerator.endElementNS(self, name, qname)

    def characters(self, content):
        if self._in_cdata:
            self._write(content.replace(']]>', '] ]>'), raw=True)
        else:
            XMLGenerator.characters(self, content)

    def comment(self, comment):
        self._write('<!-- ')
        self._write(comment.replace('-->', '- ->'), raw=True)
        self._write(' -->')

    def startCDATA(self):
        self._write('<![CDATA[')
        self._in_cdata = True

    def endCDATA(self):
        self._write(']]>')
        self._in_cdata = False

