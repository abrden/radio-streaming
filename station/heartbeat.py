from multiprocessing import Process
import time
import logging

import zmq


class Heartbeat(Process):
    def __init__(self):
        super(Heartbeat, self).__init__()
        self.logger = logging.getLogger("Heartbeat")
        self.mw = HeartbeatMiddleware()

    def run(self):
        self.mw.connect()

        self.logger.info("Starting to send heartbeats")
        while True:
            try:
                self.logger.info("Sending heartbeat")
                self.mw.send_heartbeat()
                time.sleep(5)  # Station sends a beat every 5 seconds
            except KeyboardInterrupt:
                break
        self.logger.info("End to heartbeats")


class HeartbeatMiddleware:
    def __init__(self):
        self.socket = None

    def connect(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.bind("tcp://*:6002")

    def send_heartbeat(self):
        # FIXME sending a beat for the transmitter and a beat for the receiver. Needs to be a pub-xsub
        self.socket.send_string("lubdub")
        self.socket.send_string("lubdub")
