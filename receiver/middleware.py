import logging

import zmq
from common.hearbeat_listener import HeartbeatListener
from common.ask_if_leader import AskIfLeader

class ReceiverMiddleware:
    def __init__(self, originCountry, country, freq, stations_total):
        self.logger = logging.getLogger("ReceiverMiddleware")
        self.originCountry = originCountry
        self.country = country
        self.stations_total = stations_total

        self.logger.info("Searching for leader")
        leader = AskIfLeader(originCountry, stations_total).find_leader()
        self.logger.info("Leader is %d", leader)
        self.leader_addr = "tcp://station_" + originCountry.lower() + "_" + str(leader)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.topic = country + freq
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.socket.connect(leader_addr + ":6001")
        self.logger.info("Connected to: " + leader_addr)

        self.logger.info("Starting StationHeartbeat")
        self.dead = Value('i', 0, lock=True)
        self.heartbeart_monitor = HeartbeatListener(leader_addr + ":6002", self.new_leaders_addr, self.dead)
        self.heartbeart_monitor.start()

    def receive(self):
        if self.dead.Value:
            self.logger.info("Findind new leader's address")
            leader = AskIfLeader(self.country, self.stations_total).find_leader()
            self.logger.info("Leader is %d", leader)
            self.leader_addr = "tcp://station_" + self.country.lower() + "_" + str(leader)
            
            # FIXME subscribe to leaders SUB
            self.socket = self.context.socket(zmq.SUB)
            self.socket.setsockopt(zmq.LINGER, -1)
            self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
            self.socket.connect(leader_addr + ":6001")
            self.logger.info("Connected to: " + leader_addr)

        [topic, data] = self.socket.recv_multipart()
        return data

    def close(self):
        self.socket.close()
        # TODO Terminate context
        self.heartbeart_monitor.close()
        self.heartbeart_monitor.join()

    def new_leaders_addr(self):
        return self.leader_addr + ":6002"
