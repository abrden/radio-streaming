import logging
from multiprocessing import Queue, Value, Process

import zmq

from .ring import Ring
from .answer_if_leader import AnswerIfLeader
from .heartbeat import Heartbeat
from .leaderElection import LeaderElection, WITHOUT_NEW_LEADER
from .broker import Broker

class StationMiddleware:
    def __init__(self, country, station_num, stations_total):
        self.logger = logging.getLogger("StationMiddleware")
        self.brokerIsUp = False
        self.country = country
        self.sendQueue = Queue()  # To push an item to this queue is equivalent to send a msg through the ring
        self.recvQueue = Queue()  # To pop an item from this queue is equivalente to recv a msg through the ring   
        self.leaderNews = Queue() # Notifies the results of the elections.
        self.id = station_num 
        self.broker = None
        self.stations_total = stations_total
        self.logger.info("Init leader value")
        self.leader = Value('i', WITHOUT_NEW_LEADER, lock=True)  # FIXME Initialization number??

        self.logger.info("Starting Ring")
        self.ring = Ring(country, station_num, stations_total, self.sendQueue, self.recvQueue)
        self.ring.start()

        self.logger.info("Starting AnswerIfLeader server")
        self.answer_if_leader = AnswerIfLeader(station_num, self.leader)
        self.answer_if_leader.start()

        self.logger.info("Starting leader election")
        self.leaderElection = LeaderElection(station_num, self.sendQueue, self.recvQueue, self.leaderNews)
        self.leaderElection.start()

        self.logger.info("Starting Heartbeat")
        self.heartbeat = Heartbeat()
        self.heartbeat.start()

        self.listenForChanges()
    
    def listenForChanges(self):
        while True: #TODO: Handle this graceful quit now :)
            self.leader.value = self.leaderNews.get()
            if self.leader.value == self.id and not self.brokerIsUp:
                self.broker = Broker(self.country, self.stations_total)
                self.brokerIsUp = True
                self.logger.info("START BROKER ON " + str(self.id))
                self.broker.start()
            elif self.leader.value != self.id and self.brokerIsUp:
                self.brokerIsUp = False
                self.logger.info("CLOSING BROKER ON " + str(self.id))
                self.broker.terminate()
                self.broker.join()

    def close(self):
        # TODO Terminate context
        self.heartbeat.join()
        self.ring.join()
        self.answer_if_leader.join()
    
