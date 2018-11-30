import time
import logging

import zmq

from common.hearbeat_listener import HeartbeatListener


class TransmitterMiddleware:
    def __init__(self, country, freq):
        self.logger = logging.getLogger("TransmitterMiddleware")
        self.country = country
        self.freq = freq
        
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.connect("tcp://0.0.0.0:6000")

        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener("tcp://0.0.0.0:6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

        time.sleep(2)

    def send(self, audio_chunk):
        topic = self.country + self.freq
        self.socket.send_multipart([bytes(topic, 'utf-8'), audio_chunk])

    def close(self):
        self.send(b"END")
        self.socket.close()
        # TODO Terminate context
        self.heartbeart_monitor.close()
        self.heartbeart_monitor.join()

    def new_leaders_addr(self):
        self.logger.info("Findind new leader's address")
        # TODO Find new leader
        return "tcp://0.0.0.0:6002"
