"""
ClassItem diagram item
"""

from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.i18n import _

from gaphor.diagram.classifier import ClassifierItem
from gaphor.diagram.classes.feature import AttributeItem, OperationItem

        
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
    
    __style__ = {
        'extra-space': 'compartment',
    }

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.drawing_style = self.DRAW_COMPARTMENT
        self._attributes = self.create_compartment('attributes')
        self._operations = self.create_compartment('operations')
        self._operations.use_extra_space = True

        self.watch('subject<Class>.ownedOperation', self.on_class_owned_operation)\
            .watch('subject<Class>.ownedAttribute.association', self.on_class_owned_attribute)


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
        self._operations.use_extra_space = value
        self._attributes.use_extra_space = not self._operations.visible

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
        new.register_handlers()


    def _create_operation(self, operation):
        """
        Create a new operation item.
        """
        new = OperationItem()
        new.subject = operation
        self._operations.append(new)
        new.register_handlers()

    def unregister_handlers(self):
        super(ClassItem, self).unregister_handlers()
        for a in self._attributes:
            a.unregister_handlers() 
        for o in self._operations:
            o.unregister_handlers() 

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


    def on_class_owned_attribute(self, event):
        if self.subject:
            self.sync_attributes()


    def on_class_owned_operation(self, event):
        if self.subject:
            self.sync_operations()


# vim:sw=4:et:ai
