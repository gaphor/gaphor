# vim: sw=4
# Check the attribute consistency (and proper import statements ;-) for a
# module. 

import sys
from testlist import *
from UML import *

def testvar(var1, var2):
    if isinstance(var1, Sequence):
	if var1.list[0] is not var2:
	    print "Association not fulfilled! (seq)"
	    print "var1", var1
	    print "var2", var2
	    sys.exit(1)
    else:
	if var1 is not var2:
	    print "Association not fulfilled!"
	    print "var1", var1
	    print "var2", var2
	    sys.exit(1)

for c in testlist:
    for key in c._attrdef:
        # Test associations:
	if len(c._attrdef[key]) == 3:
	    mult, c2, key2 = c._attrdef[key]
	    print c.__name__ + "." + key + " <-> " + c2.__name__ + "." + key2,
	    i1 = c()
	    i2 = c2()
	    try:
		i1.__setattr__(key, i2)
	    except AttributeError, e:
	        print "Setting value '" + key + "' on class '" + c.__name__ + "' does not seem to work."
		print e
		sys.exit(1)

	    # Now test if the keys are assigned properly
	    var1 = eval('i1.' + key)
	    var2 = eval('i2.' + key2)

	    testvar(var1, i2)
	    testvar(var2, i1)
	    print " (Okay!)"
#print "=================="
#print " All tests passed"
#print "=================="
