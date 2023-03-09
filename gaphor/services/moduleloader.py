import logging

from gaphor.abc import Service
from gaphor.entrypoint import list_entry_points

log = logging.getLogger(__name__)


class ModuleLoader(Service):
    def __init__(self):
        """Load modules defined in entrypoints `[gaphor.modules]`."""

        for ep in list_entry_points("gaphor.modules"):
            log.debug(f'found module entry point "{ep.name}"')
            ep.load()

    def shutdown(self):
        pass
