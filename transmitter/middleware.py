import zmq
import time

class TransmitterMiddleware:
    def __init__(self, country, freq):
        self.country = country
        self.freq = freq
        
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.LINGER, -1)
        self.socket.connect("tcp://0.0.0.0:6000")
        
        time.sleep(2)

    def send(self, audio_chunk):
        topic = self.country + self.freq
        self.socket.send_multipart([bytes(topic,'utf-8'),audio_chunk])

    def send_int(self, n):
        topic = self.country + self.freq
        self.socket.send_multipart([bytes(topic,'utf-8'),bytes(str(n), 'utf-8')])

    def close(self):
        self.send(b"END")
        self.socket.close()
        # TODO Terminate context
