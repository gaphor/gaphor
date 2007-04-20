
import unittest

from gaphor import resource, UML
from gaphor.application import Application
from gaphor.ui.mainwindow import MainWindow
from gaphor.diagram import items

from gaphor.actions.itemactions import *


class ItemActionTestCase(unittest.TestCase):

#    main_window = resource(MainWindow)
#    try:
#        main_window.construct()
#    except:
#        pass

    def setUp(self):
        self.diagram = UML.create(UML.Diagram)
        self.main_window.show_diagram(self.diagram)
        Application.init()
        self.main_window = Application.get_service('gui_manager').main_window

        self.class_ = self.diagram.create(items.ClassItem, subject=UML.create(UML.Class))

    def tearDown(self):
        UML.flush()
        del self.diagram
        del self.class_

    def _test_action(self, action_id):
        action = self.main_window.get_action_pool().get_action(action_id)
        assert action is not None
        action.update()
        action.execute()

    def test_ItemNewSubjectAction(self):
        self._test_action('ItemNewSubject')

    def test_AbstractClassAction(self):
        self.main_window.get_current_diagram_view().focused_item = self.class_
        self._test_action('AbstractClass')

#    def test_AbstractOperationAction(self):
#        self.main_window.get_current_diagram_view().focused_item = self.class_
#        self._test_action('AbstractOperation')

    def test_CreateAttributeAction(self):
        self.main_window.get_current_diagram_view().focused_item = self.class_
        assert not self.class_._attributes
        assert not self.class_.subject.ownedAttribute

        self._test_action('CreateAttribute')

        assert len(self.class_._attributes) == 1
        assert len(self.class_.subject.ownedAttribute) == 1

    def test_CreateOperationAction(self):
        self.main_window.get_current_diagram_view().focused_item = self.class_
        assert not self.class_._operations
        assert not self.class_.subject.ownedOperation

        self._test_action('CreateOperation')

        assert len(self.class_._operations) == 1
        assert len(self.class_.subject.ownedOperation) == 1

    def test_ShowAttributesAction(self):
        self.main_window.get_current_diagram_view().focused_item = self.class_
        self._test_action('ShowAttributes')
        assert self.class_.show_attributes

    def test_ShowOperationsAction(self):
        self.main_window.get_current_diagram_view().focused_item = self.class_
        self._test_action('ShowOperations')
        assert self.class_.show_operations


# vim:sw=4:et:ai
