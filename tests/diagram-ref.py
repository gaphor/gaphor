#!/usr/bin/env python
# vim: sw=4
#
# Check reference counting between elemens and diagram items.
#
import UML
import diagram

cnt=0
def print_hash():
    global cnt
    UML.update_model()
    cnt = len(UML.Element._hash.keys())
	#print "Element", k, ":", UML.Element._hash[k]().__dict__
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
item.get_subject().unlink()
del item
dia.unlink ()
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
dia.unlink()
item.get_subject().unlink()
del dia
print 'Unref\'ing this one will cause a core dump'
del item
print 'Hmmm... That seems not to be the problem'
print_hash()
print 'And not the assertion...'
assert (cnt == 0)
print 'OK'
