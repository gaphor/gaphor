#!/usr/bin/env python
#
# vim: sw=4

import gaphor.UML as UML
import gaphor.diagram as diagram
import gaphor.undomanager
import weakref, gobject, gc
import unittest

undo_manager = gaphor.undomanager.get_undo_manager()

class DiagramItemTestCase(unittest.TestCase):

    def setUp(self):
	undo_manager.clear_undo_stack()
	undo_manager.clear_redo_stack()
	UML.flush()

    def testUndoAttribute(self):
	c1 = UML.create(UML.Class)
	c1.name = 'one'
	undo_manager.begin_transaction()
	c1.name = 'two'
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())

	undo_manager.undo_transaction()
	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(c1.name, 'one')

	undo_manager.redo_transaction()
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(c1.name, 'two')

    def testUndoEnumeration(self):
	p = UML.create(UML.Property)
	p.aggregation = 'none'
	undo_manager.begin_transaction()
	p.aggregation = 'composite'
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())

	undo_manager.undo_transaction()
	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(p.aggregation, 'none')

	undo_manager.redo_transaction()
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(p.aggregation, 'composite')

    def testUndoAssociation_1(self):
	"""Test undo of 1:? associations."""
	p1 = UML.create(UML.Package)
	p2 = UML.create(UML.Package)
	undo_manager.begin_transaction()
	p2.package = p1
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())

	undo_manager.undo_transaction()
	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(p2.package, None)
	self.failUnlessEqual(len(p1.nestedPackage), 0)

	undo_manager.redo_transaction()
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(p2.package, p1)
	self.failUnlessEqual(len(p1.nestedPackage), 1)
	self.failUnlessEqual(p1.nestedPackage[0], p2)

    def testUndoAssociation_N(self):
	"""Test undo of n:? associations."""
	p1 = UML.create(UML.Package)
	p2 = UML.create(UML.Package)
	undo_manager.begin_transaction()
	p1.nestedPackage = p2
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())

	undo_manager.undo_transaction()
	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(p2.package, None)
	self.failUnlessEqual(len(p1.nestedPackage), 0)

	undo_manager.redo_transaction()
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(p2.package, p1)
	self.failUnlessEqual(len(p1.nestedPackage), 1)
	self.failUnlessEqual(p1.nestedPackage[0], p2)

    def testUndoElementFactory(self):
	"""Test gaphor.UML.ElementFactory."""
	self.failUnlessEqual(len(UML.select()), 0)

	undo_manager.begin_transaction()
	c = UML.create(UML.Class)
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(len(UML.select()), 1)

	undo_manager.undo_transaction()

	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(len(UML.select()), 0)

	undo_manager.redo_transaction()

	self.failIf(undo_manager.can_redo())
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(len(UML.select()), 1)

    def testUndoElementFactory_2(self):
	"""Test gaphor.UML.ElementFactory."""
	self.failUnlessEqual(len(UML.select()), 0)

	undo_manager.begin_transaction()
	c = UML.create(UML.Class)
	undo_manager.commit_transaction()

	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(len(UML.select()), 1)

	undo_manager.begin_transaction()
	o = UML.create(UML.Operation)
	c.ownedOperation = o
	undo_manager.commit_transaction()

	self.failUnlessEqual(len(UML.select()), 2)

	undo_manager.undo_transaction()

	self.failUnless(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(len(UML.select()), 1)

	undo_manager.undo_transaction()

	self.failIf(undo_manager.can_undo())
	self.failUnless(undo_manager.can_redo())
	self.failUnlessEqual(len(UML.select()), 0)

	undo_manager.redo_transaction()

	self.failUnless(undo_manager.can_redo())
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(len(UML.select()), 1)

	undo_manager.redo_transaction()

	self.failIf(undo_manager.can_redo())
	self.failUnless(undo_manager.can_undo())
	self.failUnlessEqual(len(UML.select()), 2)

# TODO: check signals.

if __name__ == '__main__':
    unittest.main()

