import logging

import zmq
from common.hearbeat_listener import HeartbeatListener

class ReceiverMiddleware:
    def __init__(self, originCountry, country, freq):
        self.logger = logging.getLogger("ReceiverMiddleware")
        self.originCountry = originCountry
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.topic = country + freq
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        antennaConnectionData = self.getConnectionDataFor(originCountry)
        self.socket.connect(antennaConnectionData)
        self.logger.info("Connected to: " + antennaConnectionData)
        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener("tcp://0.0.0.0:6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

    def getConnectionDataFor(self, originCountry):
        if originCountry == "AR":
            return "tcp://172.20.0.4:6001" #TODO: Ask stations for the leader
        else:
            return "tcp://172.20.0.3:6001"

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
