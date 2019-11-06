"""
A registry for components (e.g. services) and event handling.
"""

from typing import Iterator, Set, Tuple, Type, TypeVar
from gaphor.abc import Service
from gaphor.application import ComponentLookupError


T = TypeVar("T", bound=Service)


class ComponentRegistry(Service):
    """
    The ComponentRegistry provides a home for application wide components.
    """

    def __init__(self) -> None:
        self._comp: Set[Tuple[object, str]] = set()

    def shutdown(self) -> None:
        pass

    def get_service(self, name: str) -> Service:
        """Obtain a service used by Gaphor by name.
        E.g. service("element_factory")
        """
        return self.get(Service, name)  # type: ignore[misc]

    def register(self, component: object, name: str):
        self._comp.add((component, name))

    def unregister(self, component: object):
        self._comp = {(c, n) for c, n in self._comp if not c is component}

    def get(self, base: Type[T], name: str) -> T:
        found = {(c, n) for c, n in self._comp if isinstance(c, base) and n == name}
        if len(found) > 1:
            raise ComponentLookupError(
                f"More than one component matches {base}+{name}: {found}"
            )
        if len(found) == 0:
            raise ComponentLookupError(
                f"Component with type {base} and name {name} is not registered"
            )
        return next(iter(found))[0]

    def all(self, base: Type[T]) -> Iterator[Tuple[T, str]]:
        return ((c, n) for c, n in self._comp if isinstance(c, base))
