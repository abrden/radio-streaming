import logging

import zmq

from .heartbeat import Heartbeat


class StationMiddleware:
    def __init__(self):
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

        self.poller = zmq.Poller()
        self.poller.register(self.frontend, zmq.POLLIN)
        self.poller.register(self.backend, zmq.POLLIN)

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
