#!/usr/bin/env python

# Copyright (C) 2001-2017 Arjan Molenaar <gaphor@gmail.com>
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
Print all attributes of a specific class.
Usage: browseUML.py <Classname>
E.g. browseUML.py Class
"""

from __future__ import absolute_import
from __future__ import print_function

import sys

sys.path.append("..")

done = [object]


def print_vars(cls):
    global done
    done.append(cls)
    print(cls.__name__ + ":")
    dict = cls.__dict__
    for key in dict.keys():
        print("\t" + key + ":", str(dict[key]))
    for base in cls.__bases__:
        if base not in done:
            print_vars(base)


args = sys.argv[1:]

if args:
    cls = eval(args[0])
    print_vars(cls)
else:
    print("Usage: " + sys.argv[0] + " <UML class name>")
    sys.exit(1)
