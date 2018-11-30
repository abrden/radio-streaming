from multiprocessing import Process, Value
import logging

import zmq


class StationHeartbeat(Process):
    def __init__(self, host, dead_fun):
        super(StationHeartbeat, self).__init__()
        self.logger = logging.getLogger("StationHeartbeat")
        self.quit = Value('i', 0, lock=True)
        self.host = host
        self.dead_fun = dead_fun

    def socket_to_host(self):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, -1)
        socket.connect(self.host)
        return socket

    def run(self):
        socket = self.socket_to_host()

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        self.logger.info("Start receiving heartbeats")
        while not self.quit.value:
            socks = dict(poller.poll(15000000))  # TODO test decreasing this to see if dead_fun
            if socks:
                if socks.get(socket) == zmq.POLLIN:
                    beat = socket.recv(zmq.NOBLOCK)
                    self.logger.info("Station heartbeat received: %r", beat)
            else:
                self.logger.info("Station is dead. Finding new station's address and reconnecting")
                self.host = self.dead_fun()
                socket = self.socket_to_host()
        self.logger.info("End to heartbeats listening")

    def close(self):
        self.logger.info("Closing")
        self.quit.value = 1


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
        self.heartbeart_monitor = StationHeartbeat("tcp://0.0.0.0:6002", self.new_leaders_addr)
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
