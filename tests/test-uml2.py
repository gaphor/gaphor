from gaphor.UML.uml2 import *
c = Class()
p = Package()

print c.owner , ' == None'

c.package = p

print c.package
print c.owner
print c.namespace
