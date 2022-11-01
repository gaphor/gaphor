from dataclasses import dataclass

from gaphor.core.modeling import ElementFactory

ADD = 1
REMOVE = 2


@dataclass
class Change:
    type: int
    element_name: str
    element_type: object
    element_id: str


@dataclass
class ChangeSet:
    changes: list[Change]


def compare(current: ElementFactory, incoming: ElementFactory) -> ChangeSet:
    change_set = ChangeSet(changes=[])

    change_set.changes.extend(added_elements(current, incoming))
    return change_set


def added_elements(current: ElementFactory, incoming: ElementFactory):
    """Report elements that exist in one factory, but not in the other."""
    current_keys = set(current.keys())
    incoming_keys = set(incoming.keys())

    for key in current_keys.difference(incoming_keys):
        e = current.lookup(key)
        yield Change(
            type=REMOVE,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )

    for key in incoming_keys.difference(current_keys):
        e = incoming.lookup(key)
        yield Change(
            type=ADD,
            element_name=type(e).__name__,
            element_type=type(e),
            element_id=key,
        )
