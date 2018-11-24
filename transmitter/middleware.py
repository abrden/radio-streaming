import zmq


class TransmitterMiddleware:
    def __init__(self, country, freq):
        # TODO Do things with country and freq
        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.bind("tcp://*:5000")

    def send(self, audio_chunk):
        self.socket.send(audio_chunk)

    def send_int(self, n):
        self.socket.send_string(str(n))

    def close(self):
        self.send(b"END")
        self.socket.close()
        # TODO Terminate context
