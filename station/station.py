import logging

from .middleware import StationMiddleware
from .middleware import Retransmitter

class Station:
    def __init__(self, station_num, country, stations_total):
        self.logger = logging.getLogger("Station")
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware(station_num, country, stations_total)

    def start(self):
        self.mw.start()

    def close(self):
        self.mw.close()
        
