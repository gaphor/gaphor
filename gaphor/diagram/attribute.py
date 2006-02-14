# vim:sw=4:et
"""Attribute item.
"""

import gobject
import diacanvas

from feature import FeatureItem

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
        self._expression.set_text(self.subject.render() or '')
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
        if self.parent:
            self.parent.sync_attributes()
