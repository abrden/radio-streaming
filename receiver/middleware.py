import zmq


class ReceiverMiddleware:
    def __init__(self, country, freq):
        # TODO Do things with country and freq
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.connect("tcp://0.0.0.0:5000")

    def receive(self):
        return self.socket.recv()

    def receive_int(self):
        return int(self.socket.recv().decode())

    def close(self):
        self.socket.close()
        # TODO Terminate context
