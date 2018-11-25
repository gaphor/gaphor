# vim:sw=4:et

import sys
import xml.sax.handler
from builtins import str
from xml.sax.saxutils import escape, quoteattr

# See whether the xmlcharrefreplace error handler is
# supported
try:
    from codecs import xmlcharrefreplace_errors

    _error_handling = "xmlcharrefreplace"
    del xmlcharrefreplace_errors
except ImportError:
    _error_handling = "strict"


class XMLWriter(xml.sax.handler.ContentHandler):
    def __init__(self, out=None, encoding=None):
        if out is None:
            out = sys.stdout
        xml.sax.handler.ContentHandler.__init__(self)
        self._out = out
        self._ns_contexts = [{}]  # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]
        self._undeclared_ns_maps = []
        self._encoding = encoding or sys.getdefaultencoding()

        self._in_cdata = False
        self._in_start_tag = False
        self._next_newline = False

    def _write(self, text, start_tag=False, end_tag=False):
        """
        Write data. Tags should not be escaped. They should be marked
        by setting either ``start_tag`` or ``end_tag`` to ``True``.
        Only the tag should be marked this way. Other stuff, such as
        namespaces and attributes can be written directly to the file.
        """
        if not isinstance(text, str):
            text = text.decode(self._encoding, _error_handling)

        if self._next_newline:
            self._out.write(u"\n")
            self._next_newline = False

        if start_tag and not self._in_start_tag:
            self._in_start_tag = True
            self._out.write(u"<")
        elif start_tag and self._in_start_tag:
            self._out.write(u">")
            self._out.write(u"\n")
            self._out.write(u"<")
        elif end_tag and self._in_start_tag:
            self._out.write(u"/>")
            self._in_start_tag = False
            self._next_newline = True
            return
        elif not start_tag and self._in_start_tag:
            self._out.write(u">")
            self._in_start_tag = False
        elif end_tag:
            self._out.write(u"</")
            self._out.write(text)
            self._out.write(u">")
            self._in_start_tag = False
            self._next_newline = True
            return

        self._out.write(text)

    def _qname(self, name):
        """Builds a qualified name from a (ns_url, localname) pair"""
        if name[0]:
            # The name is in a non-empty namespace
            prefix = self._current_context[name[0]]
            if prefix:
                # If it is not the default namespace, prepend the prefix
                return prefix + ":" + name[1]
        # Return the unqualified name
        return name[1]

    # ContentHandler methods

    def startDocument(self):
        self._write(u'<?xml version="1.0" encoding="%s"?>\n' % self._encoding)

    def startPrefixMapping(self, prefix, uri):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix
        self._undeclared_ns_maps.append((prefix, uri))

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts[-1]
        del self._ns_contexts[-1]

    def startElement(self, name, attrs):
        self._write(name, start_tag=True)
        for (name, value) in list(attrs.items()):
            self._out.write(u" %s=%s" % (name, quoteattr(value)))

    def endElement(self, name):
        self._write(name, end_tag=True)

    def startElementNS(self, name, qname, attrs):
        self._write(self._qname(name), start_tag=True)

        for prefix, uri in self._undeclared_ns_maps:
            if prefix:
                self._out.write(u' xmlns:%s="%s"' % (prefix, uri))
            else:
                self._out.write(u' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        for (name, value) in list(attrs.items()):
            self._out.write(u" %s=%s" % (self._qname(name), quoteattr(value)))

    def endElementNS(self, name, qname):
        self._write(u"%s" % self._qname(name), end_tag=True)

    def characters(self, content):
        if self._in_cdata:
            self._write(content.replace(u"]]>", u"] ]>"))
        else:
            self._write(escape(content))

    def ignorableWhitespace(self, content):
        self._write(content)

    def processingInstruction(self, target, data):
        self._write(u"<?%s %s?>" % (target, data))

    def comment(self, comment):
        self._write(u"<!-- ")
        self._write(comment.replace(u"-->", u"- ->"))
        self._write(u" -->")

    def startCDATA(self):
        self._write(u"<![CDATA[")
        self._in_cdata = True

    def endCDATA(self):
        self._write(u"]]>")
        self._in_cdata = False


# vim:sw=4:et:ai
