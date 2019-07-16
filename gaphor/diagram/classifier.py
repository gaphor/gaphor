"""
Classifier diagram item.
"""

from gaphor.diagram.abc import Classified
from gaphor.diagram.compartment import CompartmentItem


class ClassifierItem(CompartmentItem, Classified):
    """
    Base class for UML classifiers.

    Classifiers can be abstract and this feature is supported by this
    class.
    """

    __style__ = {
        "name-font": "sans bold 10",
        "abstract-name-font": "sans bold italic 10",
    }

    def __init__(self, id=None, model=None):
        super(ClassifierItem, self).__init__(id, model)
        self.watch("subject<Classifier>.isAbstract", self.on_classifier_is_abstract)

    def on_classifier_is_abstract(self, event):
        self._name.font = (
            self.style.abstract_name_font
            if self.subject and self.subject.isAbstract
            else self.style.name_font
        )
        self.request_update()

    def postload(self):
        super(ClassifierItem, self).postload()
        self.on_classifier_is_abstract(None)


# vim:sw=4:et
