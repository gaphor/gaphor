#!/usr/bin/env python
#
# Test the behavior of a UML tree with a Diagram as leaf. The whole tree
# should be freed...
#
# vim: sw=4

import sys
sys.path.insert(0, '..')
import gaphor.UML as UML
import gaphor.diagram as diagram
import weakref, gobject, gc
import unittest

factory = UML.ElementFactory()
diafactory = diagram.DiagramItemFactory()

class DiagramItemTestCase(unittest.TestCase):

    def testSimpleItem(self):
	item = diagram.ActorItem()
	self.failUnless (item.subject == None)
	w_item = weakref.ref(item)
	del item
	self.failUnless (w_item() != None, gc.get_referrers(w_item()))

    def testItem2(self):
	self.failUnlessEqual(len(factory._ElementFactory__signal._Signal__signals), 0)
	gen = factory.create(UML.Generalization)
	self.failUnlessEqual(len(factory._ElementFactory__signal._Signal__signals), 0)
	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 1)
	# gen, the element factory and getrefcount()
	self.failUnlessEqual(sys.getrefcount(gen), 3)
	factory.flush()
	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 1)
	w_gen = weakref.ref(gen)
	del gen
	self.failIf(w_gen(), 'Generalization not freed')

    def testItemOnLine(self):
	self.failUnlessEqual(len(factory._ElementFactory__signal._Signal__signals), 0)
	gen = factory.create(UML.Generalization)
	self.failUnlessEqual(len(factory._ElementFactory__signal._Signal__signals), 0)
	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 1)
	# gen, the element factory and getrefcount()
	self.failUnlessEqual(sys.getrefcount(gen), 3)

	dia = factory.create(UML.Diagram)
	self.failUnlessEqual(len(dia.__dict__['__signal']._Signal__signals), 1)
	self.failUnlessEqual(sys.getrefcount(dia), 3)

	item = diafactory.create(dia, diagram.GeneralizationItem)
	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 1)
	self.failUnlessEqual(len(factory._ElementFactory__signal._Signal__signals), 0)
	self.failUnlessEqual(sys.getrefcount(dia), 3)
	self.failUnlessEqual(item.__grefcount__, 2)

#	item.set_property('subject', gen)
	self.failUnlessEqual(sys.getrefcount(gen), 3)
	item.set_subject(gen)
	self.failUnlessEqual(sys.getrefcount(gen), 4)
	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 2)
	self.failUnlessEqual(sys.getrefcount(gen), 4)
	self.failUnlessEqual(sys.getrefcount(dia), 3)

	print 'flushing...'
	factory.flush()
#	self.failUnlessEqual(len(gen.__dict__['__signal']._Signal__signals), 3)
	print 'flush done'
	w_gen = weakref.ref(gen)
	print 'del gen'
	del gen
	print 'done'
	self.failIf(w_gen(), 'Generalization not freed')

    def no_testItemOnModel(self):
	model = factory.create(UML.Model)
	# One for model, one for the factory hash (and one extra ;-)
	self.failUnlessEqual (sys.getrefcount(model), 3)
	model.name = "MyModel"
	actor = factory.create(UML.Generalization)
	actor.namespace = model
	self.failUnlessEqual (len(model.ownedElement.list), 1)
	self.failUnlessEqual (sys.getrefcount(actor), 4)
	self.failUnless (model.ownedElement.list[0] is actor)
	self.failUnless (actor.namespace is model)
	dia = factory.create(UML.Diagram)
	dia.namespace = model
	self.failUnlessEqual (sys.getrefcount(dia), 4)
	item = diafactory.create(dia, diagram.ActorItem)
	self.failUnless(item.parent is dia.canvas.root)
	self.failUnless(item.subject is not None) # New actor has been created
	self.failUnlessEqual(item.__grefcount__, 4)
	self.failUnlessEqual(sys.getrefcount(item), 8)
	item.set_property('subject', actor);
	print 'refs:', gc.get_referrers (item)

if __name__ == '__main__':
    unittest.main()

