"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

import uuid

from . import connectors, grouping
from . import (
    actions,
    classes,
    components,
    general,
    interactions,
    profiles,
    states,
    usecases,
)


def create(type):
    return create_as(type, str(uuid.uuid1()))


def create_as(type, id):
    return type(id)
