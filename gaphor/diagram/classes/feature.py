# vim:sw=4:et
"""
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
"""

from gaphor.diagram.compartment import FeatureItem
from gaphor.diagram import font


class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

        self.watch('subject<NamedElement>.name') \
            .watch('subject<Property>.isDerived') \
            .watch('subject<Property>.visibility') \
            .watch('subject<Property>.lowerValue<LiteralSpecification>.value') \
            .watch('subject<Property>.upperValue<LiteralSpecification>.value') \
            .watch('subject<Property>.defaultValue<LiteralSpecification>.value') \
            .watch('subject<Property>.typeValue<LiteralSpecification>.value')


    def postload(self):
        if self.subject:
            self.text = self.render()


class OperationItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        
        self.watch('subject<NamedElement>.name') \
            .watch('subject<Operation>.isAbstract', self.on_operation_is_abstract) \
            .watch('subject<Operation>.visibility') \
            .watch('subject<Operation>.returnResult.lowerValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.returnResult.upperValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.returnResult.typeValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.formalParameter.lowerValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.formalParameter.upperValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.formalParameter.typeValue<LiteralSpecification>.value') \
            .watch('subject<Operation>.formalParameter.defaultValue<LiteralSpecification>.value') \


    def postload(self):
        if self.subject:
            self.text = self.render()
        self.on_operation_is_abstract(None)

    def on_operation_is_abstract(self, event):
        self.font = (self.subject and self.subject.isAbstract) \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()

    def render(self):
        return self.subject.render(visibility=True, type=True, multiplicity=True, default=True) or ''


# vim:sw=4:et:ai
