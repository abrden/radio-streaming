import zmq


class ReceiverMiddleware:
    def __init__(self, country, freq):
        self.country = country
        self.freq = freq
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        topic = self.country + self.freq
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.socket.connect("tcp://0.0.0.0:6001")

    def receive(self):
        [topic, data] = self.socket.recv_multipart()
        return data

    def close(self):
        self.socket.close()
        # TODO Terminate context
