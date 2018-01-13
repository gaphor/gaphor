#!/usr/bin/env python

# Copyright (C) 2008-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
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
"""This script list classes and optionally attributes from UML model created with Gaphor."""

from __future__ import absolute_import
from __future__ import print_function

import optparse
import sys

from gaphor.UML import uml2
from gaphor import Application

# Setup command line options.
usage = 'usage: %prog [options] file.gaphor'

parser = optparse.OptionParser(usage=usage)

parser.add_option('-a', '--attributes', dest='attrs', action='store_true', help='Print class attributes')

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
    sys.exit(1)

# The model file to load.
model = args[0]

# Create the Gaphor application object.
Application.init()

# Get services we need.
element_factory = Application.get_service('element_factory')
file_manager = Application.get_service('file_manager')

# Load model from file.
file_manager.load(model)

# Find all classes using factory select.
for cls in element_factory.select(lambda e: e.isKindOf(uml2.Class)):

    print('Found class %s' % cls.name)

    if options.attrs:

        for attr in cls.ownedAttribute:
            print(' Attribute: %s' % attr.name)
