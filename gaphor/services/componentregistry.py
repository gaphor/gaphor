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
        self._comp: Set[Tuple[str, object]] = set()

    def shutdown(self) -> None:
        pass

    def get_service(self, name: str) -> Service:
        """Obtain a service used by Gaphor by name.
        E.g. service("element_factory")
        """
        return self.get(Service, name)  # type: ignore[misc] # noqa: F821

    def register(self, name: str, component: object) -> None:
        self._comp.add((name, component))

    def unregister(self, component: object) -> None:
        self._comp = {(n, c) for n, c in self._comp if c is not component}

    def get(self, base: Type[T], name: str) -> T:
        found = [(n, c) for n, c in self._comp if isinstance(c, base) and n == name]
        if len(found) > 1:
            raise ComponentLookupError(
                f"More than one component matches {base}+{name}: {found}"
            )
        if len(found) == 0:
            raise ComponentLookupError(
                f"Component with type {base} and name {name} is not registered"
            )
        return found[0][1]

    def all(self, base: Type[T]) -> Iterator[Tuple[str, T]]:
        return ((n, c) for n, c in self._comp if isinstance(c, base))
