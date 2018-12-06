import logging
from multiprocessing import Queue, Value, Process

import zmq

from .ring import Ring
from .answer_if_leader import AnswerIfLeader
from .heartbeat import Heartbeat
from .leaderElection import LeaderElection, WITHOUT_NEW_LEADER
from .broker import Broker

class Retransmitter(Process):
    def __init__(self, country,freq):
        super(Retransmitter, self).__init__()
        self.logger = logging.getLogger("Starting Retransmitter middleware")
        self.country = country
        self.freq = freq
        self.someoneListens = True
        antenaConnectionData = self.getConnectionDataFor(country)
        self.mw = RetransmitterMiddleware(antenaConnectionData)

    def getConnectionDataFor(self, country):
        return "tcp://station2:6001"

    def run(self):
        self.logger.debug("Retransmitter for country "+ self.country + " at freq " + self.freq +" started")
        self.mw.connect()
        self.mw.subscribe(self.country+self.freq)
        while self.someoneListens:
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
    def __init__(self, station_num, country, stations_total):
        self.brokerIsUp = False
        self.country = country
        self.sendQueue = Queue()  # To push an item to this queue is equivalent to send a msg through the ring
        self.recvQueue = Queue()  # To pop an item from this queue is equivalente to recv a msg through the ring   
        self.leaderNews = Queue() # Notifies the results of the elections.
        self.logger = logging.getLogger("StationMiddleware")
        self.id = station_num 
        self.broker = None
        self.leader = WITHOUT_NEW_LEADER
                        
        self.logger.info("Init leader value")
        self.leader = Value('i', 3, lock=True)

        self.logger.info("Starting Ring")
        self.ring = Ring(station_num, stations_total, self.sendQueue, self.recvQueue, self.leader)
        self.ring.start()

        self.logger.info("Starting leader election")
        self.leaderElection = LeaderElection(station_num, self.sendQueue, self.recvQueue, self.leaderNews)
        self.leaderElection.start()

        self.logger.info("Starting Heartbeat")
        self.heartbeat = Heartbeat()
        self.heartbeat.start()

        self.listenForChanges()
    
    def listenForChanges(self):
        while True: #TODO: Handle this graceful quit now :)
            self.leader = self.leaderNews.get()
            if self.leader == self.id and not self.brokerIsUp:
                self.broker = Broker(self.country)
                self.brokerIsUp = True
                self.logger.info("START BROKER ON " + str(self.id))
                self.broker.start()
            elif self.leader != self.id and self.brokerIsUp:
                self.brokerIsUp = False
                self.logger.info("CLOSING BROKER ON " + str(self.id))
                self.broker.terminate()
                self.broker.join()

    def close(self):
        # TODO Terminate context
        self.heartbeat.join()
        self.ring.join()
        self.answer_if_leader.join()
    
