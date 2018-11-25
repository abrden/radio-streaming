import logging
import wave

from .middleware import StationMiddleware

class Station:
    def __init__(self):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware()