from multiprocessing import Process
import logging

import zmq

class Broker(Process):
    def __init__(self):
        super(Broker, self).__init__()
        self.logger = logging.getLogger("Broker")
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
                self.frontend.send_multipart(message)
        self.close()
        
        def close(self):
            self.frontend.close()
            self.backend.close()
