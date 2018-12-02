import zmq
import logging 
from multiprocessing import Process

class Retransmitter(Process):
    def __init__(self, country):
        super(Retransmitter, self).__init__()
        self.logger = logging.getLogger("Starting Retransmitter middleware")
        self.country = country
        self.someoneListens = True
        antenaConnectionData = self.getConnectionDataFor(country)
        self.mw = RetransmitterMiddleware(antenaConnectionData)

    def getConnectionDataFor(self, country):
        return "tcp://station2:6001"

    def listenFor(self, freq):
        self.mw.subscribe(self.country + freq)
    
    def stopListeningFrom(self, freq):
        self.mw.unSubscribe(self.country + freq)
            
    def run(self):
        self.logger.debug("PASAMO POR ACA")
        self.mw.connect()
        self.mw.subscribe("RU100")
        while self.someoneListens:
           self.logger.debug("Listening outside countr:"+self.country)
           [topic, data] = self.mw.receive()
           self.logger.debug("Message received from:" + self.country)
           self.mw.send(topic, data)
       
    def close(self):
        self.socket.close()
        # TODO Terminate context

class RetransmitterMiddleware:
    def __init__(self, antenaConnectionData):
        self.sender = None
        self.receiver = None
        self.antenaConnectionData = antenaConnectionData

    def receive(self):
        return self.receiver.recv_multipart()
    
    def send(self, topic, data):
        self.sender.send_multipart([topic, data])

    def connect(self):
        context = zmq.Context()
        self.receiver = context.socket(zmq.SUB)
        self.receiver.setsockopt(zmq.LINGER, -1)
        self.receiver.connect(self.antenaConnectionData)
        self.sender = context.socket(zmq.PUB)
        self.sender.setsockopt(zmq.LINGER, -1)
        self.sender.connect("tcp://0.0.0.0:6000")
        
    def subscribe(self, topic):
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    def unSubscribe(self, topic):
        self.receiver.setsockopt_string(zmq.UNSUBSCRIBE, topic)
    

class StationMiddleware:
    def __init__(self, handleSubscription):
        self.context = zmq.Context()
        self.logger = logging.getLogger("StationMiddleware")

        # Init frontend (XSUB)
        self.frontend = self.context.socket(zmq.XSUB)
        self.frontend.setsockopt(zmq.LINGER, -1)
        self.frontend.bind("tcp://*:6000")
        
        # Init backend (XPUB)
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.setsockopt(zmq.LINGER, -1)
        self.backend.bind("tcp://*:6001")

        poller = zmq.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)
        
        while True:  # TODO Graceful quit
            events = dict(poller.poll(1000))
            if self.frontend in events:
                message = self.frontend.recv_multipart()
                self.logger.info("[XSUB] Message arrived:")
                self.backend.send_multipart(message)         

            if self.backend in events:
                message = self.backend.recv_multipart()
                self.logger.info("[XPUB] Message arrived: %r", message)
                handleSubscription(message)
                self.frontend.send_multipart(message)

    def close(self):
        self.frontend.close()
        self.backend.close()
        # TODO Proper closure        
