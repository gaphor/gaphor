# vim:sw=4:et
"""Operation item.
"""

import gobject
import pango
import diacanvas
from gaphor.diagram import initialize_item
from feature import FeatureItem

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

    def on_subject_notify(self, pspec, notifiers=()):
        FeatureItem.on_subject_notify(self, pspec,
                ('name', 'visibility', 'isAbstract')
                + notifiers)
        if self.subject:
            self.on_subject_notify__isAbstract(self.subject)
        # TODO: Handle subject.returnResult[*] and subject.formalParameter[*]

    def postload(self):
        FeatureItem.postload(self)
        self.on_subject_notify__isAbstract(self.subject)

    def on_subject_notify__name(self, subject, pspec):
        #log.debug('setting text %s' % self.subject.render() or '')
        self._expression.set_text(self.subject.render() or '')
        self.request_update()

    def on_subject_notify__isAbstract(self, subject, pspec=None):
        subject = self.subject
        if subject.isAbstract:
            self._expression.set_font_description(pango.FontDescription(self.FONT_ABSTRACT))
        else:
            self._expression.set_font_description(pango.FontDescription(self.FONT))
        self.request_update()

    on_subject_notify__visibility = on_subject_notify__name
    on_subject_notify__taggedValue_value = on_subject_notify__name

    def on_update(self, affine):
        # Render the operation on every update, since we can't monitor
        # the parameters and return parameters.
        self._expression.set_text(self.subject and self.subject.render() or '')
        FeatureItem.on_update(self, affine)

initialize_item(OperationItem)
