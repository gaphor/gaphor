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

done = [object]


def print_vars(cls):
    global done
    done.append(cls)
    print cls.__name__ + ":"
    dict = cls.__dict__
    for key in dict.keys():
        print "\t" + key + ":", str(dict[key])
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
