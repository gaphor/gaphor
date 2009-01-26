# vim:sw=4:et
"""
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
"""

from gaphor import UML
from gaphas.item import Item
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.diagramitem import DiagramItem
from gaphas.util import text_extents, text_set_font, text_align
from gaphor.diagram import font

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
        # Fool unlink code (attribute is not a gaphas.Item):
        self.canvas = None


    def save(self, save_func):
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
        if text:
            cr = context.cairo
            self.width, self.height = text_extents(cr, text)
        else:
            self.width, self.height = 0, 0


    def point(self, pos):
        """
        """
        return distance_rectangle_point((0, 0, self.width, self.height), pos)


class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

        self.add_watch(UML.Property.name)
        self.add_watch(UML.Property.isDerived)
        self.add_watch(UML.Property.visibility)
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


    def pre_update(self, context):
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
        
        self.add_watch(UML.Operation.name)
        self.add_watch(UML.Operation.visibility)
        self.add_watch(UML.Operation.isAbstract)
        self.add_watch(UML.Operation.taggedValue)
        # Parameters
        # TODO: Handle subject.returnResult[*] and subject.formalParameter[*]
        self.add_watch(UML.Operation.isAbstract)


    def postload(self):
        FeatureItem.postload(self)

    def pre_update(self, context):
        self.update_size(self.subject.render(), context)
        #super(OperationItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self.subject.render() or '', align_x=1, align_y=1)
        #cr.show_text(self.subject.render() or '')


class SlotItem(FeatureItem):
    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

#    def on_feature_value(self, event):
#        element = event.element
#        subject = self.subject
#        if subject and element in (subject.lowerValue, subject.upperValue, subject.defaultValue, subject.typeValue, subject.taggedValue):
#            self.request_update()


    def _render_slot(self):
        slot = self.subject
        return '%s = "%s"' % (slot.definingFeature.name, slot.value.value)

    def pre_update(self, context):
        self.update_size(self._render_slot(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self._render_slot(), align_x=1, align_y=1)


class StereotypeNameItem(FeatureItem):
    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

#    def on_feature_value(self, event):
#        element = event.element
#        subject = self.subject
#        if subject and element in (subject.lowerValue, subject.upperValue, subject.defaultValue, subject.typeValue, subject.taggedValue):
#            self.request_update()


    def _render_name(self):
        return UML.model.STEREOTYPE_FMT % self.subject.name


    def pre_update(self, context):
        self.update_size(self._render_name(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self._render_name(), align_x=0.5, align_y=0.5)


# vim:sw=4:et
