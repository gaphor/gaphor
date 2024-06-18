"""A registry for components (e.g. services) and event handling."""

import functools
import inspect
from typing import Iterator, List, Tuple, Type, TypeVar

from gaphor.abc import Service

T = TypeVar("T", bound=Service)


class ComponentLookupError(LookupError):
    pass


class ComponentRegistry(Service):
    """The ComponentRegistry provides a home for application wide
    components."""

    def __init__(self) -> None:
        self._comp: List[Tuple[str, object]] = []

    def shutdown(self) -> None:
        pass

    def get_service(self, name: str) -> Service:
        """Obtain a service used by Gaphor by name.

        E.g. service("element_factory")
        """
        return self.get(Service, name)  # type: ignore[type-abstract] # noqa: F821

    def register(self, name: str, component: object) -> None:
        self._comp.append((name, component))

    def unregister(self, component: object) -> None:
        self._comp = [(n, c) for n, c in self._comp if c is not component]

    def get(self, base: Type[T], name: str) -> T:
        found = [(n, c) for n, c in self._comp if isinstance(c, base) and n == name]
        if len(found) > 1:
            raise ComponentLookupError(
                f"More than one component matches {base}+{name}: {found}"
            )
        if not found:
            raise ComponentLookupError(
                f"Component with type {base} and name {name} is not registered"
            )
        return found[0][1]

    def all(self, base: Type[T]) -> Iterator[Tuple[str, T]]:
        return ((n, c) for n, c in self._comp if isinstance(c, base))

    def partial(self, func):
        """Return a new function with partial application of services."""
        kwargs = {}

        for param_name, _param in inspect.signature(func).parameters.items():
            found = [(n, c) for n, c in self._comp if n == param_name]
            if len(found) > 1:
                raise ComponentLookupError(
                    f"More than one component matches {param_name}: {found}"
                )
            if found:
                kwargs[param_name] = found[0][1]

        return functools.partial(func, **kwargs)
