#!/usr/bin/env python
# vim: sw=4
#
# Check reference counting between elemens and diagram items.
#
import UML
import diagram
import gc

cnt=0
def print_hash():
    global cnt
    cnt = 0
    UML.gc()
    for k in UML.Element._hash.keys():
	#print "Element", k, ":", UML.Element._hash[k]().__dict__
        cnt += 1
    #else:
        #print "No elements in hash."

print "Creating diagram:"
dia = diagram.Diagram()
print_hash()
assert (cnt == 1)

print "Creating item:"
item = dia.create_item (diagram.Actor)
print_hash()
assert (cnt == 2)

print "Deleting created items:"
del item
del dia
print_hash()
assert (cnt == 0)

print "Creating diagram:"
dia = diagram.Diagram()
print_hash()
assert (cnt == 1)

print "Creating item:"
item = dia.create_item (diagram.Actor)
print_hash()
assert (cnt == 2)

print "Deleting created items:"
del dia
del item # Unreffing this one will cause a core dump
print_hash()
assert (cnt == 0)

