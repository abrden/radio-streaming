from multiprocessing import Process, Value
import logging
import time

import zmq


class Heartbeat(Process):
    def __init__(self):
        super(Heartbeat, self).__init__()
        self.logger = logging.getLogger("Heartbeat")

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.setsockopt(zmq.LINGER, -1)
        socket.bind("tcp://*:6002")

        self.logger.info("Starting to send heartbeats")
        while True:
            try:
                self.logger.info("Sending heartbeat")
                socket.send_string("lubdub")
                time.sleep(5)
            except KeyboardInterrupt:
                break
        self.logger.info("End to heartbeats")


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
