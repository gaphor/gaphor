#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
import sys
from xml.sax.saxutils import escape, quoteattr
import xml.sax.handler

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
        self._ns_contexts = [{}] # contains uri -> prefix dicts
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
        if self._next_newline:
            self._out.write('\n')
            self._next_newline = False

        if start_tag and not self._in_start_tag:
            self._in_start_tag = True
            self._out.write('<')
        elif start_tag and self._in_start_tag:
            self._out.write('>')
            self._out.write('\n')
            self._out.write('<')
        elif end_tag and self._in_start_tag:
            self._out.write('/>')
            self._in_start_tag = False
            self._next_newline = True
            return
        elif not start_tag and self._in_start_tag:
            self._out.write('>')
            self._in_start_tag = False
        elif end_tag:
            self._out.write('</')
            self._out.write(text)
            self._out.write('>')
            self._in_start_tag = False
            self._next_newline = True
            return
            
        if isinstance(text, str):
            self._out.write(text)
        else:
            self._out.write(text.encode(self._encoding, _error_handling))

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
        self._write('<?xml version="1.0" encoding="%s"?>\n' %
                        self._encoding)

    def startPrefixMapping(self, prefix, uri):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix
        self._undeclared_ns_maps.append((prefix, uri))

    def endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts[-1]
        del self._ns_contexts[-1]

    def startElement(self, name, attrs):
        self._write(name, start_tag=True)
        for (name, value) in attrs.items():
            self._out.write(' %s=%s' % (name, quoteattr(value)))

    def endElement(self, name):
        self._write(name, end_tag=True)

    def startElementNS(self, name, qname, attrs):
        self._write(self._qname(name), start_tag=True)

        for prefix, uri in self._undeclared_ns_maps:
            if prefix:
                self._out.write(' xmlns:%s="%s"' % (prefix, uri))
            else:
                self._out.write(' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            self._out.write(' %s=%s' % (self._qname(name), quoteattr(value)))

    def endElementNS(self, name, qname):
        self._write('%s' % self._qname(name), end_tag=True)

    def characters(self, content):
        if self._in_cdata:
            self._write(content.replace(']]>', '] ]>'))
        else:
            self._write(escape(content))

    def ignorableWhitespace(self, content):
        self._write(content)

    def processingInstruction(self, target, data):
        self._write('<?%s %s?>' % (target, data))

    def comment(self, comment):
        self._write('<!-- ')
        self._write(comment.replace('-->', '- ->'))
        self._write(' -->')

    def startCDATA(self):
        self._write('<![CDATA[')
        self._in_cdata = True

    def endCDATA(self):
        self._write(']]>')
        self._in_cdata = False


# vim:sw=4:et:ai
