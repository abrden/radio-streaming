import logging

import zmq


class AskIfLeader:
    def __init__(self, stations_total):
        super(AskIfLeader, self).__init__()
        self.logger = logging.getLogger("AskIfLeader")
        self.stations_total = stations_total
        self.client = None

    def connect_to_station(self, station_num):
        self.logger.info("Setting up socket")
        context = zmq.Context()
        self.client = context.socket(zmq.REQ)
        self.client.setsockopt(zmq.LINGER, -1)
        self.client.connect("tcp://station" + str(station_num) + ":6005")

    def find_leader(self):
        leader = -1
        for i in range(1, self.stations_total + 1):
            self.logger.info("Connecting to station %d", i)
            self.connect_to_station(i)
            self.logger.info("Asking if it is leader")
            self.client.send_string("Are you leader?")
            ans = self.client.recv()
            if ans.decode() == "Yes":
                self.logger.info("Station %d is the leader", i)
                leader = i
                self.client.close()
                break
            self.client.close()
        self.logger.info("Returning leader %d", leader)
        return leader
