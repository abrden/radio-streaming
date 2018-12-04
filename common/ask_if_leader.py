from multiprocessing import Process
import logging

import zmq


class AskIfLeader(Process):  # TODO Who uses this?
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
        self.client.connect("tcp://station"+ str(station_num) + ":6005")

    def run(self):
        leader = -1
        for i in range(self.stations_total):
            self.connect_to_station(i)
            self.client.send_string("Are you leader?")
            ans = self.client.recv()
            if ans.decode() == "Yes":
                leader = i
            self.client.close()
        return leader
