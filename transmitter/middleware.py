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
        antennaConnectionData = self.getConnectionDataFor(country)
        self.socket.connect(antennaConnectionData)
        self.logger.info("Connected to: " + antennaConnectionData)
        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener("tcp://0.0.0.0:6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

    def getConnectionDataFor(self, country):
        if country == "AR":
            return "tcp://172.20.0.4:6000" #TODO: Ask stations for the leader
        else:
            return "tcp://172.20.0.3:6000"

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
