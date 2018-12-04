import zmq
import socket
socket.gethostbyname(socket.gethostname())

class ReceiverMiddleware:
    def __init__(self, originCountry, country, freq):
        self.country = country
        self.originCountry = originCountry
        self.freq = freq
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        topic = self.country + self.freq
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        antennaConnectionData = self.getConnectionDataFor(originCountry)
        self.socket.connect(antennaConnectionData)

    def getConnectionDataFor(self, originCountry):
        if originCountry == "AR":
            return "tcp://172.20.0.3:6001" #TODO: Ask stations for the leader
        else:
            return "tcp://172.20.0.2:6001"

    def receive(self):
        [topic, data] = self.socket.recv_multipart()
        return data

    def close(self):
        self.socket.close()
        # TODO Terminate context
