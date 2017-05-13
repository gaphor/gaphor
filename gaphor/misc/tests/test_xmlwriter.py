#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
import sys
import unittest
from gaphor.misc.xmlwriter import XMLWriter

class Writer:
    def __init__(self):
        self.s = ''

    def write(self, text):
        self.s += text


class XMLWriterTestCase(unittest.TestCase):

    def test_elements_1(self):
        w = Writer()
        xml_w = XMLWriter(w)
        xml_w.startDocument()
        xml_w.startElement('foo', {})
        xml_w.endElement('foo')

        xml = """<?xml version="1.0" encoding="%s"?>\n<foo/>""" % sys.getdefaultencoding()
        assert w.s == xml, w.s + ' != ' + xml

    def test_elements_2(self):
        w = Writer()
        xml_w = XMLWriter(w)
        xml_w.startDocument()
        xml_w.startElement('foo', {})
        xml_w.startElement('bar', {})
        xml_w.endElement('bar')
        xml_w.endElement('foo')

        xml = """<?xml version="1.0" encoding="%s"?>\n<foo>\n<bar/>\n</foo>""" % sys.getdefaultencoding()
        assert w.s == xml, w.s

    def test_elements_test(self):
        w = Writer()
        xml_w = XMLWriter(w)
        xml_w.startDocument()
        xml_w.startElement('foo', {})
        xml_w.startElement('bar', {})
        xml_w.characters('hello')
        xml_w.endElement('bar')
        xml_w.endElement('foo')

        xml = """<?xml version="1.0" encoding="%s"?>\n<foo>\n<bar>hello</bar>\n</foo>""" % sys.getdefaultencoding()
        assert w.s == xml, w.s

    def test_elements_ns_default(self):
        w = Writer()
        xml_w = XMLWriter(w)
        xml_w.startDocument()
        xml_w.startPrefixMapping(None, 'http://gaphor.devjavu.com/schema')
        xml_w.startElementNS(('http://gaphor.devjavu.com/schema', 'foo'), 'qn', {})
        xml_w.endElementNS(('http://gaphor.devjavu.com/schema', 'foo'), 'qn')

        xml = """<?xml version="1.0" encoding="%s"?>\n<foo xmlns="http://gaphor.devjavu.com/schema"/>""" % sys.getdefaultencoding()
        assert w.s == xml, w.s

    def test_elements_ns_1(self):
        w = Writer()
        xml_w = XMLWriter(w)
        xml_w.startDocument()
        xml_w.startPrefixMapping('g', 'http://gaphor.devjavu.com/schema')
        xml_w.startElementNS(('http://gaphor.devjavu.com/schema', 'foo'), 'qn', {})
        xml_w.endElementNS(('http://gaphor.devjavu.com/schema', 'foo'), 'qn')

        xml = """<?xml version="1.0" encoding="%s"?>\n<g:foo xmlns:g="http://gaphor.devjavu.com/schema"/>""" % sys.getdefaultencoding()
        assert w.s == xml, w.s


# vim:sw=4:et:ai
