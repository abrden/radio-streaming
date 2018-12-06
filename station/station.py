import logging

from .middleware import StationMiddleware


class Station:
    def __init__(self, country, station_num, stations_total):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware(country, station_num, stations_total)

    def start(self):
        self.mw.start()

    def close(self):
        self.mw.close()
