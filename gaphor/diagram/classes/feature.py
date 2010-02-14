# vim:sw=4:et
"""
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
"""

from gaphor.diagram.compartment import FeatureItem
from gaphor.diagram import font
from gaphor import UML


class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        super(AttributeItem, self).__init__()


class OperationItem(FeatureItem):

    def __init__(self, id=None):
        super(OperationItem, self).__init__()


    def on_operation_is_abstract(self, event):
        self.font = (self.subject and self.subject.isAbstract) \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()


    def render(self):
        return UML.format(self.subject, visibility=True, type=True, multiplicity=True, default=True) or ''


# vim:sw=4:et:ai
