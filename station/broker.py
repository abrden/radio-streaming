from multiprocessing import Process
import logging

import zmq

class Broker(Process):
    def __init__(self, country):
        super(Broker, self).__init__()
        self.logger = logging.getLogger("Broker")
        self.country = country
        self.listenersAnotherCountry = {}
        self.retransmitters = {}
        self.frontend = None
        self.backend = None
        self.poller = None
        
    def run(self):
        context = zmq.Context()
        self.logger.info("Setting up XPUB-XSUB")
        # Init frontend (XSUB)
        self.frontend = context.socket(zmq.XSUB)
        self.frontend.setsockopt(zmq.LINGER, -1)
        self.frontend.bind("tcp://*:6000")
        
        # Init backend (XPUB)
        self.backend = context.socket(zmq.XPUB)
        self.backend.setsockopt(zmq.LINGER, -1)
        self.backend.bind("tcp://*:6001")

        self.poller = zmq.Poller()
        self.poller.register(self.frontend, zmq.POLLIN)
        self.poller.register(self.backend, zmq.POLLIN)
        self.logger.info("Broker initialized")
        while True: #TODO: Pseudo Graceful quit needed (cause it is terminated by mean dad)
            events = dict(self.poller.poll(1000))
            if self.frontend in events:
                message = self.frontend.recv_multipart()
                self.logger.info("[XSUB] Message arrived")
                self.backend.send_multipart(message)
            if self.backend in events:
                message = self.backend.recv_multipart()
                self.logger.info("[XPUB] Message arrived")
                self.handleSubscription(message)
                self.frontend.send_multipart(message)
        self.close()
        
    def close(self):
        self.frontend.close()
        self.backend.close()
        self.closeRetransmissions()

    def handleSubscription(self, subActivity):
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

    def closeRetransmissions(self):
        for topic, value in self.listenersAnotherCountry.items():
            self.stopListeningFor(topic)
            self.listenersAnotherCountry.pop(topic, None)
