"""GTK-based types.

Thos module is normally imported in the method where it's used to avoid
the need for a global import of GTK.
"""

from gaphor import UML
from gaphor.core.format import format, parse
from gaphor.diagram.gtkmodels import EditableTreeModel
from gaphor.transaction import transactional


class ClassAttributes(EditableTreeModel):
    """GTK tree model to edit class attributes."""

    def __init__(self, item):
        super().__init__(item, cols=(str, bool, object))

    def get_rows(self):
        for attr in self._item.subject.ownedAttribute:
            if not attr.association:
                yield [format(attr, note=True), attr.isStatic, attr]

    def create_object(self):
        attr = self._item.model.create(UML.Property)
        self._item.subject.ownedAttribute = attr
        return attr

    @transactional
    def set_object_value(self, row, col, value):
        attr = row[-1]
        if col == 0:
            parse(attr, value)
            row[0] = format(attr, note=True)
        elif col == 1:
            attr.isStatic = not attr.isStatic
            row[1] = attr.isStatic
        elif col == 2:
            # Value in attribute object changed:
            row[0] = format(attr, note=True)
            row[1] = attr.isStatic

    def swap_objects(self, o1, o2):
        return self._item.subject.ownedAttribute.swap(o1, o2)

    def sync_model(self, new_order):
        self._item.subject.ownedAttribute.order(
            lambda e: new_order.index(e) if e in new_order else len(new_order)
        )


class ClassOperations(EditableTreeModel):
    """GTK tree model to edit class operations."""

    def __init__(self, item):
        super().__init__(item, cols=(str, bool, bool, object))

    def get_rows(self):
        for operation in self._item.subject.ownedOperation:
            yield [
                format(operation, note=True),
                operation.isAbstract,
                operation.isStatic,
                operation,
            ]

    def create_object(self):
        operation = self._item.model.create(UML.Operation)
        self._item.subject.ownedOperation = operation
        return operation

    @transactional
    def set_object_value(self, row, col, value):
        operation = row[-1]
        if col == 0:
            parse(operation, value)
            row[0] = format(operation, note=True)
        elif col == 1:
            operation.isAbstract = not operation.isAbstract
            row[1] = operation.isAbstract
        elif col == 2:
            operation.isStatic = not operation.isStatic
            row[2] = operation.isStatic
        elif col == 3:
            row[0] = format(operation, note=True)
            row[1] = operation.isAbstract
            row[2] = operation.isStatic

    def swap_objects(self, o1, o2):
        return self._item.subject.ownedOperation.swap(o1, o2)

    def sync_model(self, new_order):
        self._item.subject.ownedOperation.order(new_order.index)


class ClassEnumerationLiterals(EditableTreeModel):
    """GTK tree model to edit enumeration literals."""

    def __init__(self, item):
        super().__init__(item, cols=(str, object))

    def get_rows(self):
        for literal in self._item.subject.ownedLiteral:
            yield [format(literal), literal]

    def create_object(self):
        literal = self._item.model.create(UML.EnumerationLiteral)
        self._item.subject.ownedLiteral = literal
        literal.enumeration = self._item.subject
        return literal

    @transactional
    def set_object_value(self, row, col, value):
        literal = row[-1]
        if col == 0:
            parse(literal, value)
            row[0] = format(literal)
        elif col == 1:
            # Value in attribute object changed:
            row[0] = format(literal)

    def swap_objects(self, o1, o2):
        return self._item.subject.ownedLiteral.swap(o1, o2)

    def sync_model(self, new_order):
        self._item.subject.ownedLiteral.order(new_order.index)
