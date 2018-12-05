import logging

from .middleware import StationMiddleware


class Station:
    def __init__(self, station_num, stations_total):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware(station_num, stations_total)

    def start(self):
        self.mw.start()

    def close(self):
        self.mw.close()
