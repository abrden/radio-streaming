import logging
from multiprocessing import Process
from common.hearbeat_listener import HeartbeatListener
from common.ask_if_leader import AskIfLeader

import zmq

class Retransmitter(Process):
    def __init__(self, country,freq, stations_total):
        super(Retransmitter, self).__init__()
        self.logger = logging.getLogger("Starting Retransmitter middleware")
        self.country = country
        self.freq = freq
        self.someoneListens = True
        self.mw = RetransmitterMiddleware(country, stations_total)

    def run(self):
        self.logger.debug("Retransmitter for country "+ self.country + " at freq " + self.freq +" started")
        self.mw.connect()
        self.mw.subscribe(self.country+self.freq)
        while self.someoneListens:
           [topic, data] = self.mw.receive()
           self.logger.debug("Retransmit message from:" + self.country)
           self.mw.send(topic, data)
       
    def close(self):
        self.socket.close()
        # TODO Terminate context

class RetransmitterMiddleware:
    def __init__(self, country, stations_total):
        self.country = country
        self.stations_total = stations_total
        self.sender = None
        self.receiver = None
        self.logger = logging.getLogger("Starting Retransmitter middleware deep")

    def receive(self):
        return self.receiver.recv_multipart()
    
    def send(self, topic, data):
        self.sender.send_multipart([topic, data])

    def connect(self):
        context = zmq.Context()
        self.receiver = context.socket(zmq.SUB)
        self.receiver.setsockopt(zmq.LINGER, -1)
        leader = AskIfLeader(self.country, self.stations_total).find_leader()
        self.logger.info("Leader is %d", leader)
        leader_addr = "tcp://station_" + self.country.lower() + "_" + str(leader)
        
        self.receiver.connect(leader_addr+":6001")
        self.sender = context.socket(zmq.PUB)
        self.sender.setsockopt(zmq.LINGER, -1)
        self.sender.connect("tcp://0.0.0.0:6000")
        
        self.logger.info("Starting StationHeartbeat")
        self.heartbeart_monitor = HeartbeatListener(leader_addr + ":6002", self.new_leaders_addr)
        self.heartbeart_monitor.start()

    def subscribe(self, topic):
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    def unSubscribe(self, topic):
        self.receiver.setsockopt_string(zmq.UNSUBSCRIBE, topic)

    def new_leaders_addr(self):
        self.logger.info("Findind new leader's address")
        leader = AskIfLeader(self.country, self.stations_total).find_leader()
        self.logger.info("Leader is %d", leader)
        leader_addr = "tcp://station_" + self.country.lower() + "_" + str(leader)
        # FIXME subscribe to leaders SUB
        return leader_addr + ":6001"    