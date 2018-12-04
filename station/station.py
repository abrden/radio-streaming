import logging

from .middleware import StationMiddleware


class Station:
    def __init__(self):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware()

    def start(self):
        self.mw.start()

    def close(self):
        self.mw.close()