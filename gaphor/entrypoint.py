import inspect
import logging
from typing import Dict, Type, TypeVar

import importlib_metadata

T = TypeVar("T")

logger = logging.getLogger(__name__)


def initialize(scope, services=None, **known_services: T) -> Dict[str, T]:
    return init_entrypoints(load_entrypoints(scope, services), **known_services)


def load_entrypoints(scope, services=None) -> Dict[str, Type[T]]:
    """
    Load services from resources.
    """
    uninitialized_services = {}
    for ep in importlib_metadata.entry_points()[scope]:
        cls = ep.load()
        if not services or ep.name in services:
            logger.debug(f'found service entry point "{ep.name}"')
            uninitialized_services[ep.name] = cls
    return uninitialized_services


def init_entrypoints(
    uninitialized_services: Dict[str, Type[T]], **known_services: T
) -> Dict[str, T]:
    """
    Instantiate service definitions, taking into account dependencies
    defined in the constructor.

    Given a dictionary `{name: service-class}`,
    return a map `{name: service-instance}`.
    """
    ready: Dict[str, T] = dict(known_services)

    def pop(name):
        try:
            return uninitialized_services.pop(name)
        except KeyError:
            return None

    def init(name, cls):
        kwargs = {}
        for dep in inspect.signature(cls).parameters:
            if dep not in ready:
                depcls = pop(dep)
                if depcls:
                    kwargs[dep] = init(dep, depcls)
                else:
                    logger.info(
                        f"Entrypont {name} parameter {dep} does not reference a resolved dependency"
                    )
            else:
                kwargs[dep] = ready[dep]
        srv = cls(**kwargs)
        ready[name] = srv
        return srv

    while uninitialized_services:
        name = next(iter(uninitialized_services.keys()))
        cls = pop(name)
        init(name, cls)

    return ready
