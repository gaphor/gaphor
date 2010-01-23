"""
Classifier diagram item.
"""

from gaphor.diagram.compartment import CompartmentItem
from gaphor.diagram.font import FONT_ABSTRACT_NAME, FONT_NAME


class ClassifierItem(CompartmentItem):
    """
    Base class for UML classifiers.

    Classifiers can be abstract and this feature is supported by this
    class.
    """
    def __init__(self, id=None):
        super(ClassifierItem, self).__init__(id)
        self.watch('subject<Classifier>.isAbstract', self.on_classifier_is_abstract)


    def on_classifier_is_abstract(self, event):
        self._name.font = FONT_ABSTRACT_NAME \
                if self.subject and self.subject.isAbstract \
                else FONT_NAME
        self.request_update()


    def postload(self):
        super(ClassifierItem, self).postload()
        self.on_classifier_is_abstract(None)


# vim:sw=4:et
