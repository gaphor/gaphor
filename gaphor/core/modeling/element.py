#!/usr/bin/env python
"""Base class for model elements."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING

from gaphor.core.modeling.base import Base
from gaphor.core.modeling.properties import (
    attribute,
    relation_many,
    relation_one,
)

if TYPE_CHECKING:
    from gaphor.core.modeling.coremodel import (
        Comment,
        Dependency,
        Namespace,
        Relationship,
    )
    from gaphor.core.modeling.diagram import Diagram
    from gaphor.core.modeling.presentation import Presentation

log = logging.getLogger(__name__)


__all__ = ["Element", "self_and_owners"]


def self_and_owners(element: Element | None) -> Iterator[Element]:
    """Return the element and the ancestors (Element.owner)."""
    seen = set()
    e = element
    while e:
        if e in seen:
            return
        yield e
        seen.add(e)
        e = e.owner


class Element(Base):
    name: attribute[str] = attribute("name", str)
    note: attribute[str] = attribute("note", str)
    comment: relation_many[Comment]
    ownedDiagram: relation_many[Diagram]
    ownedElement: relation_many[Element]
    owner: relation_one[Element]
    presentation: relation_many[Presentation]
    relationship: relation_many[Relationship]
    sourceRelationship: relation_many[Relationship]
    targetRelationship: relation_many[Relationship]
    clientDependency: relation_many[Dependency]
    supplierDependency: relation_many[Dependency]
    memberNamespace: relation_one[Namespace]
    namespace: relation_one[Namespace]

    # From UML:
    appliedStereotype: relation_many[Element]

    @property
    def qualifiedName(self) -> list[str]:
        """Returns the qualified name of the element as a list."""
        qname = [e.name or "??" for e in self_and_owners(self)]
        qname.reverse()
        return qname
