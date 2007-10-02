# vim:sw=4:et
'''
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
'''

from gaphor import UML
from gaphas.item import Item
from diagramitem import DiagramItem
from gaphor.diagram import DiagramItemMeta
from gaphas.util import text_extents, text_set_font, text_align
import font

class FeatureItem(DiagramItem):
    """
    FeatureItems are model elements who recide inside a ClassifierItem, such
    as methods and attributes. Those items can have comments attached, but only
    on the left and right side.
    Note that features can also be used inside objects.
    """

    def __init__(self, id=None):
        DiagramItem.__init__(self, id)
        self.width = 0
        self.height = 0
        self.text = ''
        # Fool unlink code:
        self.canvas = None
        self.need_sync = False


    def save(self, save_func):
#        for prop in ('affine',):
#            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)
        
    def postload(self):
        if self.subject:
            self._expression.set_text(self.subject.render())

    def get_size(self, update=False):
        """
        Return the size of the feature. If update == True the item is
        directly updated.
        """
        return self.width, self.height

    def get_text(self):
        return ''

    def update_size(self, text, context):
        cr = context.cairo
        self.width, self.height = text_extents(cr, text)

#    def on_subject_notify(self, pspec, notifiers=()):
#        DiagramItem.on_subject_notify(self, pspec, notifiers)
#        #log.debug('setting text %s' % self.subject.render() or '')
#        self.text = self.subject and self.subject.render() or ''

    def point(self, x, y):
        """
        """
        return distance_rectangle_point((0, 0, self.width, self.height), (x, y))


class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        self.need_sync = False

        self.add_watch(UML.Property.name)
        self.add_watch(UML.Property.isDerived)
        self.add_watch(UML.Property.visibility)
        self.add_watch(UML.Property.association, self.on_property_association)
        self.add_watch(UML.Property.lowerValue)
        self.add_watch(UML.Property.upperValue)
        self.add_watch(UML.Property.defaultValue)
        self.add_watch(UML.Property.typeValue)
        self.add_watch(UML.Property.taggedValue)
        self.add_watch(UML.LiteralSpecification.value, self.on_feature_value)

    def on_feature_value(self, event):
        element = event.element
        subject = self.subject
        if subject and element in (subject.lowerValue, subject.upperValue, subject.defaultValue, subject.typeValue, subject.taggedValue):
            self.request_update()


    def on_property_association(self, event):
        """
        Make sure we update the attribute compartment (in case
        the class_ property was defined before it is connected to
        an association.
        """
        if event.element is self.subject:
            self.need_sync = True
            self.request_update()

    def pre_update(self, context):
        self.need_sync = False
        self.update_size(self.subject.render(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self.subject.render() or '', align_x=1, align_y=1)


# TODO: handle Parameter's

class OperationItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        self.need_sync = False
        
        self.add_watch(UML.Operation.name)
        self.add_watch(UML.Operation.visibility)
        self.add_watch(UML.Operation.isAbstract)
        self.add_watch(UML.Operation.taggedValue)
        # Parameters
        # TODO: Handle subject.returnResult[*] and subject.formalParameter[*]
        self.add_watch(UML.Operation.isAbstract)


    def postload(self):
        FeatureItem.postload(self)
        self.need_sync = False

    def pre_update(self, context):
#        if self.need_sync and context.parent:
#            context.parent.sync_operations()
        self.need_sync = False
        self.update_size(self.subject.render(), context)
        #super(OperationItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self.subject.render() or '', align_x=1, align_y=1)
        #cr.show_text(self.subject.render() or '')


# vim:sw=4:et
