import logging
from multiprocessing import Queue, Value

import zmq

from .ring import Ring
from .answer_if_leader import AnswerIfLeader
from .heartbeat import Heartbeat
from .leaderElection import LeaderElection

class StationMiddleware:
    def __init__(self, station_num, stations_total):
        self.logger = logging.getLogger("StationMiddleware")

        self.logger.info("Setting up XPUB-XSUB")
        context = zmq.Context()

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

        self.logger.info("Init message queue")
        self.sendQueue = Queue()  # To push an item to this queue is equivalent to send a msg through the ring
        self.recvQueue = Queue()

        self.logger.info("Init leader value")
        self.leader = Value('i', 3, lock=True)

        self.logger.info("Starting Ring")
        self.ring = Ring(station_num, stations_total, self.sendQueue, self.recvQueue, self.leader)
        self.ring.start()

        self.logger.info("Starting leader election")
        self.leaderElection = LeaderElection(station_num, self.sendQueue, self.recvQueue)
        self.leaderElection.begin()

        self.logger.info("Starting Heartbeat")
        self.heartbeat = Heartbeat()
        self.heartbeat.start()
                
    def start(self):
        while True:  # TODO Graceful quit
            events = dict(self.poller.poll(1000))
            if self.frontend in events:
                message = self.frontend.recv_multipart()
                self.logger.info("[XSUB] Message arrived")
                self.backend.send_multipart(message)
            if self.backend in events:
                message = self.backend.recv_multipart()
                self.logger.info("[XPUB] Message arrived")
                self.frontend.send_multipart(message)

    def close(self):
        self.frontend.close()
        self.backend.close()
       
        # TODO Terminate context
        self.heartbeat.join()
        self.ring.join()
        self.answer_if_leader.join()
