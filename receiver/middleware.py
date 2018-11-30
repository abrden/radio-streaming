import logging

import zmq

from common.hearbeat_listener import HeartbeatListener


class ReceiverMiddleware:
    def __init__(self, country, freq):
        self.logger = logging.getLogger("ReceiverMiddleware")
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.topic = country + freq
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.socket.connect("tcp://0.0.0.0:6001")

        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener("tcp://0.0.0.0:6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

    def receive(self):
        [topic, data] = self.socket.recv_multipart()
        return data

    def close(self):
        self.socket.close()
        # TODO Terminate context
        self.heartbeart_monitor.close()
        self.heartbeart_monitor.join()

    def new_leaders_addr(self):
        self.logger.info("Findind new leader's address")
        # TODO Find new leader
        return "tcp://0.0.0.0:6002"
