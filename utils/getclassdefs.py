import sys
sys.path.append('../build/lib')

import gaphor.UML as UML
import gaphor.storage as storage

file = sys.argv[1]
names = sys.argv[2:]
storage.load(file)
#clear()
select = GaphorResource(UML.ElementFactory).select

for c in select(lambda e: e.isKindOf(UML.Class) and e.name in names):
    print 'Class:', c.name
    if c.feature:
	print 'Attributes'
    for a in c.feature:
	print '\t%s' % a.name
    if c.association:
	print 'Associations'
    for a in c.association:
	for con in a.association.connection:
	    if con is not a and con.isNavigable:
		print '\t%s: %s[%s] %s' % (con.name, con.participant.name, con.multiplicity, a.aggregation)
    print

