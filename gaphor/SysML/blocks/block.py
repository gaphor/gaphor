from gaphor.UML.classes import ClassItem


class BlockItem(ClassItem):
    def additional_stereotypes(self):
        return ["block"]
