#!/usr/bin/python

"""
This script list classes and optionally attributes from UML model created
with Gaphor.
"""

import gaphor
from gaphor.storage import storage
import gaphor.UML as UML

import optparse
import sys

usage = 'usage: %prog [options] file.gaphor'

parser = optparse.OptionParser(usage=usage)

parser.add_option('-a', '--attributes', dest='attrs', action='store_true',
    help='print classes attributes')

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
    sys.exit(1)

model = args[0]

# create UML object factory
factory = UML.ElementFactory()

# load model from file
storage.load(model, factory)

# find all classes using factory
for cls in factory.select(lambda e: e.isKindOf(UML.Class)):
    print 'found class %s' % cls.name
    if options.attrs:
        for attr in cls.ownedAttribute:
            print ' attr: %s' % attr.name

# vim:sw=4:et:ai
