"""ClassItem diagram item
"""
# vim:sw=4:et

# TODO: make loading of features work (adjust on_groupable_add)
#       probably best to do is subclass Feature in OperationItem and A.Item

import gobject
import diacanvas

from gaphor import UML
from gaphor.i18n import _

from classifier import ClassifierItem
from attribute import AttributeItem
from operation import OperationItem

from gaphor.interfaces import IClassView
from zope import interface
        
class ClassItem(ClassifierItem, diacanvas.CanvasGroupable):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments (Compartment): one for
    attributes and one for operations. To add and remove such features
    the ClassItem implements the CanvasGroupable interface.
    Items can be added by callling class.add() and class.remove().
    This is used to handle CanvasItems, not UML objects!
    """
    interface.implements(IClassView)

    __uml__ = UML.Class, UML.Stereotype
    __stereotype__ = {
        'stereotype': UML.Stereotype,
         'metaclass': (UML.Class, lambda self: hasattr(self.subject, 'extension') and self.subject.extension),
    }
    
    __gproperties__ = {
        'show-attributes': (gobject.TYPE_BOOLEAN, 'show attributes',
                            '',
                            1, gobject.PARAM_READWRITE),
        'show-operations': (gobject.TYPE_BOOLEAN, 'show operations',
                            '',
                            1, gobject.PARAM_READWRITE),
    }

    popup_menu = ClassifierItem.popup_menu + (
        'separator',
        'AbstractClass',
        'Fold',
        'separator',
        'CreateAttribute',
        'CreateOperation',
        'separator',
        'ShowAttributes',
        'ShowOperations',
        'separator',
        'CreateLinks',
        '<ClassPopupSlot>'
    )

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self._attributes = self.create_compartment('attributes')
        self._operations = self.create_compartment('operations')

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'show-attributes')
        self.save_property(save_func, 'show-operations')
        ClassifierItem.save(self, save_func)

    def postload(self):
        ClassifierItem.postload(self)
        self.sync_attributes()
        self.sync_operations()


    def do_set_property(self, pspec, value):
        if pspec.name == 'show-attributes':
            self.preserve_property('show-attributes')
            self._attributes.visible = value
            self.request_update()
        elif pspec.name == 'show-operations':
            self.preserve_property('show-operations')
            self._operations.visible = value
            self.request_update()
        else:
            ClassifierItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'show-attributes':
            return self._attributes.visible
        elif pspec.name == 'show-operations':
            return self._operations.visible
        return ClassifierItem.do_get_property(self, pspec)

    def _create_attribute(self, attribute):
        """Create a new attribute item.
        """
        new = AttributeItem()
        new.subject = attribute
        self.add(new)

    def _create_operation(self, operation):
        """Create a new operation item.
        """
        new = OperationItem()
        new.subject = operation
        self.add(new)

    def sync_attributes(self):
        """Sync the contents of the attributes compartment with the data
        in self.subject.
        """
        owned_attributes = [a for a in self.subject.ownedAttribute if not a.association]
        #log.debug('sync_attributes %s' % owned_attributes)
        self.sync_uml_elements(owned_attributes, self._attributes,
                           self._create_attribute)

    def sync_operations(self):
        """Sync the contents of the operations compartment with the data
        in self.subject.
        """
        self.sync_uml_elements(self.subject.ownedOperation, self._operations,
                           self._create_operation)


    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        ClassifierItem.on_subject_notify(self, pspec,
                                    ('ownedAttribute', 'ownedOperation') + notifiers)
        # Create already existing attributes and operations:
        if self.subject:
            self.sync_attributes()
            self.sync_operations()
        self.request_update()

    def on_subject_notify__ownedAttribute(self, subject, pspec=None):
        """Called when the ownedAttribute property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedAttribute')
        # Filter attributes that are connected to an association:
        self.preserve_property('width')
        self.preserve_property('height')
        self.sync_attributes()

    def on_subject_notify__ownedOperation(self, subject, pspec=None):
        """Called when the ownedOperation property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedOperation')
        self.preserve_property('width')
        self.preserve_property('height')
        self.sync_operations()

    # Groupable

    def on_groupable_add(self, item):
        """Add an attribute or operation.
        """
        #if isinstance(item.subject, UML.Property):
        if isinstance(item, AttributeItem):
            # TODO: check if property not already in attribute list
            #log.debug('Adding attribute %s' % item)
            if not self._attributes.has_item(item):
                #log.debug('Adding attribute really %s' % item)
                self._attributes.append(item)
                item.set_child_of(self)
        #elif isinstance(item.subject, UML.Operation):
        elif isinstance(item, OperationItem):
            #log.debug('Adding operation %s' % item)
            if not self._operations.has_item(item):
                self._operations.append(item)
                item.set_child_of(self)
        else:
            log.warning('feature %s is not a Feature' % item)
            return 0
        self.request_update()
        return 1

    def on_groupable_remove(self, item):
        """Remove a feature subitem.
        """
        if item in self._attributes:
            #print 'remove attr:', item
            self._attributes.remove(item)
            item.set_child_of(None)
        elif item in self._operations:
            self._operations.remove(item)
            item.set_child_of(None)
        else:
            log.warning('feature %s not found in feature list' % item)
            return 0
        self.request_update()
        #log.debug('Feature removed: %s' % item)
        return 1

    def on_groupable_iter(self):
        for i in self._attributes:
            yield i
        for i in self._operations:
            yield i
