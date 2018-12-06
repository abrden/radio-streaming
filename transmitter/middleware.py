import logging

import zmq

from common.hearbeat_listener import HeartbeatListener
from common.ask_if_leader import AskIfLeader


class TransmitterMiddleware:
    def __init__(self, country, freq, stations_total):
        self.logger = logging.getLogger("TransmitterMiddleware")

        self.country = country
        self.stations_total = stations_total

        self.logger.info("Searching for leader")
        leader = AskIfLeader(country, stations_total).find_leader()
        self.logger.info("Leader is %d", leader)
        leader_addr = "tcp://station_" + country.lower() + "_" + str(leader)

        self.country = country
        self.freq = freq
        
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.connect(leader_addr + ":6000")
        self.logger.info("Connected to: " + leader_addr)

        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener(leader_addr + ":6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

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
        leader = AskIfLeader(self.country, self.stations_total).find_leader()
        self.logger.info("Leader is %d", leader)
        leader_addr = "tcp://station_" + self.country.lower() + "_" + str(leader)
        # FIXME PUB on new leader
        return leader_addr + ":6002" #TODO: Esto no seria 6000?
