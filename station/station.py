import logging

from .middleware import StationMiddleware
from .middleware import Retransmitter

class Station:
    def __init__(self, country):
        self.logger = logging.getLogger("Station")
        self.country = country
        self.listenersAnotherCountry = {}
        self.retransmitters = {}
        self.logger.debug("Starting middleware")
        self.mw = StationMiddleware(self.handleSubscriptions)
        
    def handleSubscriptions(self, subActivity):
        isASubscription = subActivity[0][0] == 1
        country = subActivity[0][1:3].decode() # Country codes of len = 2
        freq = subActivity[0][3:].decode()
        if self.country != country:
            topic = country + freq
            if isASubscription:
                self.logger.debug("New subscription for another country arrived")
                if topic in self.listenersAnotherCountry:
                    self.listenersAnotherCountry[topic] += 1
                else:
                    self.listenersAnotherCountry[topic] = 1
                    self.startListeningFor(country, freq)
            else:
                if topic in self.listenersAnotherCountry:
                    self.listenersAnotherCountry[topic] -= 1
                    if self.listenersAnotherCountry[topic] == 0:
                        self.stopListeningFrom(country, freq)
                        self.listenersAnotherCountry.pop(topic, None)
                
    def startListeningFor(self, country, freq):
        self.logger.debug("Start listening in country:" + country + " and freq:" + freq)
        self.retransmitters[country+freq] = Retransmitter(country,freq)
        self.retransmitters[country+freq].start()

    def stopListeningFrom(self, country, freq):        
        self.retransmitters[country+freq].terminate()
        self.retransmitters[country+freq].join()