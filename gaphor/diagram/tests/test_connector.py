#!/usr/bin/env python

# Copyright (C) 2009-2017 Arjan Molenaar <gaphor@gmail.com>
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
"""
Test connector item.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.connector import ConnectorItem
from gaphor.tests.testcase import TestCase


class ConnectorItemTestCase(TestCase):
    """
    Connector item basic tests.
    """
    def test_create(self):
        """Test creation of connector item
        """
        conn = self.create(ConnectorItem, uml2.Connector)
        self.assertFalse(conn.subject is None)
        #self.assertTrue(conn.end is None)


    def test_name(self):
        """Test connected interface name
        """
        conn = self.create(ConnectorItem, uml2.Connector)
        end = self.element_factory.create(uml2.ConnectorEnd)
        iface = self.element_factory.create(uml2.Interface)
        end.role = iface
        conn.subject.end = end
        #conn.end = end
        #self.assertTrue(conn._end is end)

        self.assertEquals('', conn._interface.text)

        iface.name = 'RedSea'
        self.assertEquals('RedSea', conn._interface.text)


    def test_setting_end(self):
        """Test creation of connector item
        """
        conn = self.create(ConnectorItem, uml2.Connector)
        end = self.element_factory.create(uml2.ConnectorEnd)
        iface = self.element_factory.create(uml2.Interface)
        end.role = iface
        iface.name = 'RedSea'
        conn.subject.end = end
        #conn.end = end
        #self.assertTrue(conn._end is end)
        self.assertEquals('RedSea', conn._interface.text)

        del conn.subject.end[end]
        conn.end = None
        self.assertEquals('', conn._interface.text)


    def test_persistence(self):
        """Test connector item saving/loading
        """
        conn = self.create(ConnectorItem, uml2.Connector)

        end = self.element_factory.create(uml2.ConnectorEnd)
        #conn.end = end

        data = self.save()
        self.assertTrue(end.id in data)

        self.load(data)

        connectors = self.diagram.canvas.select(lambda e: isinstance(e, ConnectorItem))
        ends = self.kindof(uml2.ConnectorEnd)
        #self.assertTrue(connectors[0].end is not None)
        #self.assertTrue(connectors[0].end is ends[0])



# vim:sw=4:et:ai
