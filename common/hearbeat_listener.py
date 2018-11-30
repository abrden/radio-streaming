from multiprocessing import Process, Value
import logging

import zmq


class HeartbeatListener(Process):
    def __init__(self, host, dead_fun):
        super(HeartbeatListener, self).__init__()
        self.logger = logging.getLogger("HeartbeatListener")
        self.quit = Value('i', 0, lock=True)
        self.dead_fun = dead_fun

        self.socket = None
        self.connect(host)

    def connect(self, host):
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket.connect(host)

    def reconnect(self, host):
        self.socket.close()
        self.connect(host)

    def run(self):
        self.logger.info("Start receiving heartbeats")
        while not self.quit.value:
            self.logger.info("Receiving")
            beat = self.socket.recv()
            if beat:
                self.logger.info("Station heartbeat received: %r", beat)
            else:
                self.logger.info("Station is dead. Finding new station's address and reconnecting")
                host = self.dead_fun()
                self.reconnect(host)
        self.logger.info("End to heartbeats listening")

    def close(self):
        self.logger.info("Closing")
        self.quit.value = 1


class HeartbeatListenerMiddleware: # Unused
    def __init__(self, host):
        self.logger = logging.getLogger("HeartbeatListenerMiddleware")
        self.socket = None
        self.connect(host)

    def connect(self, host):
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.socket.connect(host)

    def reconnect(self, host):
        self.socket.close()
        self.connect(host)

    def receive_heartbeat(self):
        self.logger.info("Receiving")
        return self.socket.recv()
