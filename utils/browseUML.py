#!/usr/bin/env python
#
# Print all attributes of a specific class.
#
# Usage: browseUML.py <Classname>
# E.g. browseUML.py Class
#
# Arjan Molenaar.

import sys

sys.path.append("..")

from gaphor.UML import *

done = [ object ]
def print_vars(cls):
    global done
    done.append(cls)
    print cls.__name__ + ":"
    dict = cls._attrdef
    for key in dict.keys():
        print "\t" + key + ":",
	if type(dict[key][0]) is type(Sequence):
	    print "Sequence of " + dict[key][1].__name__,
	else:
	    print "Instance of " + dict[key][1].__name__,
	if len(dict[key]) > 2:
	    print "( <-> " + dict[key][2] + ")"
	else:
	    print ""
    for base in cls.__bases__:
	if base not in done:
	    print_vars(base)

args = sys.argv[1:]

if args:
    cls = eval(args[0])
    print_vars(cls)
else:
    print "Usage: " + sys.argv[0] + " <UML class name>"
    sys.exit(1)
