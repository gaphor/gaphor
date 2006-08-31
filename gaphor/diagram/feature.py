# vim:sw=4:et
'''
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
'''

from gaphas.item import Item
from diagramitem import DiagramItem
from gaphor.undomanager import undoable
from gaphor.diagram import DiagramItemMeta


class FeatureItem(DiagramItem):
    """FeatureItems are model elements who recide inside a ClassifierItem, such
    as methods and attributes. Those items can have comments attached, but only
    on the left and right side.
    Note that features can also be used inside objects.
    """

    FONT='sans 10'

    def __init__(self, id=None):
        DiagramItem.__init__(self, id)
        self.width = 0
        self.height = 0
        self.text = ''


    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def save(self, save_func):
        for prop in ('affine',):
            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)
        
    def postload(self):
        if self.subject:
            self._expression.set_text(self.subject.render())

    def get_size(self, update=False):
        """Return the size of the feature. If update == True the item is
        directly updated.
        """
        return self.width, self.height

    def get_text(self):
        return ''

    def update_size(self, text, context):
        cr = context.cairo
        x_bear, y_bear, self.width, self.height, x_adv, y_adv = cr.text_extents(text)

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramItem.on_subject_notify(self, pspec, notifiers)
        #log.debug('setting text %s' % self.subject.render() or '')
        self.text = self.subject and self.subject.render() or ''

    # CanvasItem callbacks:

    def point(self, x, y):
        """
        """
        return distance_rectangle_point((0, 0, self.width, self.height), (x, y))

    # Editable

    def on_editable_get_editable_shape(self, x,y):
        return self._expression

    def on_editable_start_editing(self, shape):
        #self.preserve_property('expression')
        pass

    def on_editable_editing_done(self, shape, new_text):
        self.set_property('expression', new_text)
        #if new_text != self.subject.name:
        #    self.subject.name = new_text
        self.request_update()




from zope import interface
from gaphor.interfaces import IAttributeView

class AttributeItem(FeatureItem):
    interface.implements(IAttributeView)

    popup_menu = FeatureItem.popup_menu + (
        'EditItem',
        'DeleteAttribute',
        'MoveUp',
        'MoveDown',
        'separator',
        'CreateAttribute',
    )

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        self.need_sync_attributes = False

    def on_subject_notify(self, pspec, notifiers=()):
        FeatureItem.on_subject_notify(self, pspec, ('name',
                                                    'isDerived',
                                                    'visibility',
                                                    'lowerValue.value',
                                                    'upperValue.value',
                                                    'defaultValue.value',
                                                    'typeValue.value',
                                                    'taggedValue',
                                                    'association')
                                                    + notifiers)
        #self._expression.set_text(self.subject.render() or '')
        #self.request_update()

    def on_subject_notify__name(self, subject, pspec):
        #log.debug('setting text %s' % self.subject.render() or '')
        #self._expression.set_text(self.subject.render() or '')
        self.request_update()

    on_subject_notify__isDerived = on_subject_notify__name
    on_subject_notify__visibility = on_subject_notify__name
    on_subject_notify__lowerValue_value = on_subject_notify__name
    on_subject_notify__upperValue_value = on_subject_notify__name
    on_subject_notify__defaultValue_value = on_subject_notify__name
    on_subject_notify__typeValue_value = on_subject_notify__name
    on_subject_notify__taggedValue = on_subject_notify__name

    def on_subject_notify__association(self, subject, pspec):
        """Make sure we update the attribute compartment (in case
        the class_ property was defined before it is connected to
        an association.
        """
        #if self.parent:
        #    self.parent.sync_attributes()
        self.need_sync_attributes = True
        self.request_update()

    def pre_update(self, context):
        if self.need_sync_attributes and content.parent:
            context.parent.sync_attributes()
        self.need_sync_attributes = False
        self.update_size(self.subject.render(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = content.cairo
        cr.show_text(self.subject.render() or '')



# TODO: handle Parameter's

class OperationItem(FeatureItem):

    popup_menu = FeatureItem.popup_menu + (
        'AbstractOperation',
        'EditItem',
        'DeleteOperation',
        'MoveUp',
        'MoveDown',
        'separator',
        'CreateOperation'
    )

    FONT_ABSTRACT='sans italic 10'

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        self.need_sync_operations = False

    def on_subject_notify(self, pspec, notifiers=()):
        FeatureItem.on_subject_notify(self, pspec,
                        ('name', 'visibility', 'isAbstract')
                        + notifiers)

        # TODO: Handle subject.returnResult[*] and subject.formalParameter[*]

    def postload(self):
        FeatureItem.postload(self)
        self.need_sync_operations = False

    def on_subject_notify__name(self, subject, pspec):
        #log.debug('setting text %s' % self.subject.render() or '')
        self.request_update()

    on_subject_notify__isAbstract = on_subject_notify__name
    on_subject_notify__visibility = on_subject_notify__name
    on_subject_notify__taggedValue = on_subject_notify__name

    def pre_update(self, context):
        if self.need_sync_operations and content.parent:
            context.parent.sync_operations()
        self.need_sync_operations = False
        self.update_size(self.subject.render(), context)
        #super(OperationItem, self).pre_update(context)

    def draw(self, context):
        cr = content.cairo
        cr.show_text(self.subject.render() or '')


# vim:sw=4:et
