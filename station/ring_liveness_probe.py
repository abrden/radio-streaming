from threading import Thread
from multiprocessing import Process
import logging
import time

import zmq


class NextAsker(Process):
    def __init__(self, station_num, stations_total):
        super(NextAsker, self).__init__()
        self.logger = logging.getLogger("NextAsker")
        self.station_num = station_num
        self.stations_total = stations_total
        self.stations_conns = {}
        self.answerer = PreviousAnswerer(self.station_num, self.stations_total, self.stations_conns)

    def connect_to_ring_pals(self): # FIXME
        context = zmq.Context()
        if self.station_num == 1:
            conns = {}
            self.logger.info("Binding for station %d", 2)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6003")
            conns[2] = socket

            self.logger.info("Binding for station %d", 3)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6004")
            conns[3] = socket

            self.stations_conns[self.station_num] = conns

            self.logger.info("Connecting to station %d", 2)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station2:6004")
            self.stations_conns[2] = socket

            self.logger.info("Connecting to station %d", 3)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station3:6003")
            self.stations_conns[3] = socket

        elif self.station_num == 2:
            conns = {}
            self.logger.info("Binding for station %d", 1)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6004")
            conns[2] = socket

            self.logger.info("Binding for station %d", 3)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6003")
            conns[3] = socket

            self.stations_conns[self.station_num] = conns

            self.logger.info("Connecting to station %d", 3)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station3:6004")
            self.stations_conns[3] = socket

            self.logger.info("Connecting to station %d", 1)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station1:6003")
            self.stations_conns[1] = socket

        elif self.station_num == 3:
            conns = {}
            self.logger.info("Binding for station %d", 1)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6003")
            conns[1] = socket

            self.logger.info("Binding for station %d", 2)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.bind("tcp://*:6004")
            conns[2] = socket

            self.stations_conns[self.station_num] = conns

            self.logger.info("Connecting to station %d", 1)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station1:6004")
            self.stations_conns[1] = socket

            self.logger.info("Connecting to station %d", 2)
            socket = context.socket(zmq.PAIR)
            socket.setsockopt(zmq.RCVTIMEO, 10000)
            socket.setsockopt(zmq.SNDTIMEO, 10000)
            socket.setsockopt(zmq.LINGER, -1)
            socket.connect("tcp://station2:6003")
            self.stations_conns[2] = socket
        self.logger.info("Stations connections %r", self.stations_conns)

    def next_station(self):
        return self.next_station_to(self.station_num)

    def next_station_to(self, station_num):
        if station_num + 1 <= self.stations_total:
            return station_num + 1
        else:
            return 1

    def previous_station(self):
        if self.station_num - 1 > 0:
            return self.station_num - 1
        else:
            return self.stations_total

    def send_live_probe(self):
        next = self.next_station()
        self.logger.info("Sending live probe msg to station %d", next)
        socket = self.stations_conns[self.station_num][next]
        try:
            socket.send_string("Alive?")
            self.logger.info("Waiting for live probe response from station %d", next)
            msg = socket.recv()
            if msg.decode() == "I'm alive":
                self.logger.info("Response received")
                return True
        except zmq.error.Again:
            self.logger.info("Timeout. Response not received")
            return False

    def bypass_next_station(self):
        self.logger.info("Bypassing next node")
        next = self.next_station()
        nextnext = self.next_station_to(next)
        self.logger.info("Nextnext is %d", nextnext)
        if nextnext == self.station_num:
            self.logger.info("Nextnext is me")
            return  # FIXME wat do i do here
        socket = self.stations_conns[self.station_num][nextnext]
        socket.send_string("I'm your new previous")
        self.logger.info("Overwriting next and prev stations")
        self.stations_conns[self.station_num][next] = socket
        prev = self.previous_station()
        self.stations_conns[self.station_num][prev] = socket
        self.logger.info("Stations connections %r", self.stations_conns)

    def run(self):
        self.connect_to_ring_pals()
        self.answerer.start()

        while True: # TODO graceful quit
            ok = self.send_live_probe()
            if not ok:
                self.bypass_next_station()
            time.sleep(5)

        self.answerer.join()


class PreviousAnswerer(Thread):
    def __init__(self, station_num, stations_total, stations_conns):
        super(PreviousAnswerer, self).__init__()
        self.logger = logging.getLogger("PreviousAnswerer")
        self.station_num = station_num
        self.stations_total = stations_total
        self.stations_conns = stations_conns

    def previous_station(self):
        if self.station_num - 1 > 0:
            return self.station_num - 1
        else:
            return self.stations_total

    def answer_live_probe(self):
        prev = self.previous_station()
        socket = self.stations_conns[prev]
        self.logger.info("Waiting live probe msg from station %d on socket %r", prev, socket)
        try:
            msg = socket.recv()
            self.logger.info("Received msg from live probe: %r", msg)
            if msg.decode() == "Alive?":
                self.logger.info("Answering I'm alive")
                socket.send_string("I'm alive")
            if msg.decode == "I'm your new previous":
                self.logger.info("I have a new previous")
        except zmq.error.Again:
            self.logger.info("Timed out waiting for msg from %d to answer", prev)
            return # Timeout to continue with the loop

    def run(self):
        while True: # TODO graceful quit
            self.answer_live_probe()
