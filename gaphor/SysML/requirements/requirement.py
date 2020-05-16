from gaphor.UML.classes import ClassItem


class RequirementItem(ClassItem):
    def additional_stereotypes(self):
        return ["requirement"]
