#!/usr/bin/env python

# Validate an Gaphor XML file using the Gaphor DTD

import libxml2 as xml
import sys

dtd = xml.parseDTD(None, '../doc/gaphor.dtd')

doc = xml.parseFile ('../gaphor/a.xml')

newdtd = doc.newDtd ('gaphor', None, '../doc/gaphor.dtd')

doc.addChild (newdtd)

doc.saveFormatFile ('-',  2)
