# vim:sw=4:et
"""Attribute item.
"""

import gobject
import diacanvas
from gaphor.diagram import initialize_item

from feature import FeatureItem

class AttributeItem(FeatureItem):

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
                                                    'taggedValue.value')
                                                    + notifiers)

    def on_subject_notify__name(self, subject, pspec):
        self._expression.set_text(self.subject.render())
        self.request_update()

    on_subject_notify__isDerived = on_subject_notify__name
    on_subject_notify__visibility = on_subject_notify__name
    on_subject_notify__lowerValue_value = on_subject_notify__name
    on_subject_notify__upperValue_value = on_subject_notify__name
    on_subject_notify__defaultValue_value = on_subject_notify__name
    on_subject_notify__typeValue_value = on_subject_notify__name
    on_subject_notify__taggedValue_value = on_subject_notify__name


initialize_item(AttributeItem)
