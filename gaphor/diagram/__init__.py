"""
The diagram package contains items (to be drawn on the diagram), tools
(used for interacting with the diagram) and interfaces (used for adapting the
diagram).
"""

import uuid

import gaphor.diagram.actions
import gaphor.diagram.classes
import gaphor.diagram.components
import gaphor.diagram.general
import gaphor.diagram.interactions
import gaphor.diagram.profiles
import gaphor.diagram.states
import gaphor.diagram.usecases


def create(type, factory):
    return create_as(type, str(uuid.uuid1()), factory)


def create_as(type, id, factory):
    return type(id, factory)
