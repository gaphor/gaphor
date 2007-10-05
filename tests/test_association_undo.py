"""
This test exhibits a bug (ticket 77) that occurs when an undo action is done
after an association is disconnected from a class.


See: http://gaphor.devjavu.com/ticket/77
"""

import unittest

from zope import component
from gaphor import UML
from gaphor import transaction
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect
from gaphor.application import Application

class AssociationUndoTestCase(unittest.TestCase):
    
    def setUp(self):
        Application.init(services=['adapter_loader', 'element_factory', 'undo_manager'])

    def tearDown(self):
        Application.shutdown()

    def testAssociationUndo(self):
        factory = Application.get_service('element_factory')

        diagram = factory.create(UML.Diagram)
        
        class1 = factory.create(UML.Class)
        class1.name = 'class1'
        classItem1 = diagram.create(items.ClassItem, subject=class1)

        class2 = factory.create(UML.Class)
        class2.name = 'class2'
        classItem2 = diagram.create(items.ClassItem, subject=class2)
        
        assoc = diagram.create(items.AssociationItem)
        assert assoc.subject is None

        adapter = component.queryMultiAdapter((classItem1, assoc), IConnect)
        assert adapter
        adapter.connect(assoc.handles()[0])
        
        adapter = component.queryMultiAdapter((classItem2, assoc), IConnect)
        assert adapter
        adapter.connect(assoc.handles()[1])
        
        assert assoc.subject
        assert assoc.head_end.subject
        assert assoc.tail_end.subject

        former = (assoc.subject, assoc.head_end.subject, assoc.tail_end.subject)
        
        tx = transaction.Transaction()
        
        adapter = component.queryMultiAdapter((classItem2, assoc), IConnect)
        assert adapter
        adapter.disconnect(assoc.handles()[1])
        
        tx.commit()

        assert assoc.subject is None
        assert assoc.head_end.subject is None
        assert assoc.tail_end.subject is None

        undo_manager = Application.get_service('undo_manager')

        assert undo_manager.can_undo()

        undo_manager.undo_transaction()

        assert not undo_manager.can_undo()

        assert assoc.subject is former[0]
        assert assoc.head_end.subject is former[1]
        assert assoc.tail_end.subject is former[2]

        

if __name__ == '__main__':
    unittest.main()

# vim:sw=4:et:ai
