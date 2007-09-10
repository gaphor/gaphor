"""
ClassItem diagram item
"""

from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.i18n import _

from classifier import ClassifierItem
from feature import AttributeItem, OperationItem

        
class ClassItem(ClassifierItem):
    """
    This item visualizes a Class instance.

    A ClassItem contains two compartments (Compartment): one for
    attributes and one for operations. To add and remove such features
    the ClassItem implements the CanvasGroupable interface.
    Items can be added by callling class.add() and class.remove().
    This is used to handle CanvasItems, not UML objects!
    """

    __uml__ = UML.Class, UML.Stereotype
    __stereotype__ = {
        'stereotype': UML.Stereotype,
         'metaclass': lambda self: (not isinstance(self.subject, UML.Stereotype)) and hasattr(self.subject, 'extension') and self.subject.extension,
    }
    
    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self._attributes = self.create_compartment('attributes')
        self._operations = self.create_compartment('operations')

        self.add_watch(UML.Class.ownedAttribute)
        self.add_watch(UML.Class.ownedOperation)

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

    @observed
    def _set_show_operations(self, value):
            self._operations.visible = value

    show_operations = reversible_property(fget=lambda s: s._operations.visible,
                               fset=_set_show_operations)

    @observed
    def _set_show_attributes(self, value):
        self._attributes.visible = value

    show_attributes = reversible_property(fget=lambda s: s._attributes.visible,
                               fset=_set_show_attributes)

    def _create_attribute(self, attribute):
        """
        Create a new attribute item.
        """
        new = AttributeItem()
        new.subject = attribute
        self._attributes.append(new)

    def _create_operation(self, operation):
        """
        Create a new operation item.
        """
        new = OperationItem()
        new.subject = operation
        self._operations.append(new)

    def sync_attributes(self):
        """
        Sync the contents of the attributes compartment with the data
        in self.subject.
        """
        owned_attributes = [a for a in self.subject.ownedAttribute if not a.association]
        #log.debug('sync_attributes %s' % owned_attributes)
        self.sync_uml_elements(owned_attributes, self._attributes,
                           self._create_attribute)

    def sync_operations(self):
        """
        Sync the contents of the operations compartment with the data
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
        """
        Called when the ownedAttribute property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedAttribute')
        self.sync_attributes()

    def on_subject_notify__ownedOperation(self, subject, pspec=None):
        """
        Called when the ownedOperation property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedOperation')
        self.sync_operations()

    def pre_update(self, context):
        if self._attributes.need_sync:
            self.sync_attributes()
        if self._operations.need_sync:
            self.sync_operations()
        super(ClassItem, self).pre_update(context)


# vim:sw=4:et:ai
