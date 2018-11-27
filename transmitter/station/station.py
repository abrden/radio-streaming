import logging

from .middleware import StationMiddleware


class Station:
    def __init__(self, country):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Start with country: %s", country)

        self.country = country

        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware(country)

    def start(self):
        self.logger.debug("Never gets here")



