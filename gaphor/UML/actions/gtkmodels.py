from gaphor import UML
from gaphor.core.format import format, parse
from gaphor.diagram.gtkmodels import EditableTreeModel
from gaphor.transaction import transactional


class ActivityParameters(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def __init__(self, item):
        super().__init__(item, cols=(str, object))

    def get_rows(self):
        for node in self._item.subject.node:
            if isinstance(node, UML.ActivityParameterNode):
                yield [format(node.parameter), node]

    def create_object(self):
        model = self._item.model
        node = model.create(UML.ActivityParameterNode)
        node.parameter = model.create(UML.Parameter)
        self._item.subject.node = node
        return node

    @transactional
    def set_object_value(self, row, col, value):
        node = row[-1]
        if col == 0:
            parse(node.parameter, value)
            row[0] = format(node.parameter)
        elif col == 1:
            # Value in attribute object changed:
            row[0] = format(node.parameter)

    def swap_objects(self, o1, o2):
        return self._item.subject.node.swap(o1, o2)

    def sync_model(self, new_order):
        self._item.subject.node.order(
            lambda key: new_order.index(key) if key in new_order else -1
        )
