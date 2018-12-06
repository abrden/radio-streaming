from multiprocessing import Process
import logging

import zmq


class AnswerIfLeader(Process):
    def __init__(self, station_num, leader):
        super(AnswerIfLeader, self).__init__()
        self.logger = logging.getLogger("AnswerIfLeader")
        self.station_num = station_num
        self.leader = leader
        self.server = None

    def setup_server(self):
        self.logger.info("Setting up server")
        context = zmq.Context()
        self.server = context.socket(zmq.REP)
        self.server.setsockopt(zmq.LINGER, -1)
        self.server.bind("tcp://*:6005")

    def run(self):
        self.setup_server()

        while True:  # FIXME Graceful quit
            msg = self.server.recv()
            if msg.decode() == "Are you leader?":
                if self.station_num == self.leader.value:
                    self.server.send_string("Yes")
                else:
                    self.server.send_string("No")

        self.server.close()
