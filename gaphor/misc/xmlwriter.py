# vim:sw=4:et

import sys
from xml.sax.saxutils import XMLGenerator

class XMLWriter(XMLGenerator):
    """An XMLGenerator with CDATA handling extensions.
    """

    def __init__(self, out=None):
        XMLGenerator.__init__(self, out, sys.getdefaultencoding())
        self._in_cdata = False

    def characters(self, content):
        if self._in_cdata:
            self._out.write(content.replace(']]>', '] ]>'))
        else:
            XMLGenerator.characters(self, content)

    # Lexical handler methods

    def comment(self, comment):
        self._out.write('<!-- ')
        self._out.write(comment.replace('-->', '- ->'))
        self._out.write(' -->')

    def startCDATA(self):
        self._out.write('<![CDATA[')
        self._in_cdata = True

    def endCDATA(self):
        self._out.write(']]>')
        self._in_cdata = False

