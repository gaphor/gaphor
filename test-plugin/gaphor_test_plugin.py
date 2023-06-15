import logging

from gaphor.abc import Service

log = logging.getLogger(__name__)


class TestService(Service):
    def __init__(self):
        log.info("Initializing test service")

    def shutdown(self):
        log.info("Shutting down test service")
