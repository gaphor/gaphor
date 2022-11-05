from gaphor.abc import Service
from gaphor.entrypoint import initialize


class ModuleLoader(Service):
    def __init__(self):
        """Load modules defined in entrypoints `[gaphor.modules]`."""

        initialize("gaphor.modules")

    def shutdown(self):
        pass
